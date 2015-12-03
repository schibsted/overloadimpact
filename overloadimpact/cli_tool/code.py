#!/usr/bin/env python
import loadimpact
import time
import os
import re
import datastore
import requests
import stat
import liclient
import paths

TEMP_DIR = '/tmp/oimp'

imports = {}


def __process_datastores(code, last_data_store_versions):
    regex = r'datastore.open\(\'(.*)-DS_VERSION\'\)'
    matches = re.findall(regex, code, re.M | re.I)

    if matches:
        suffix = '-DS_VERSION'
        for match in matches:
            holder = match + suffix
            latest = last_data_store_versions[match]
            latest = latest.encode('ascii', 'ignore')  # convert to ascii to match holder, this was not needed before :(
            print '    Using datastore %s' % latest
            code = code.replace(holder, latest)

    return code


def __load_imports(filename, code):
    regex = r'(--- import (.*))'
    matches = re.findall(regex, code, re.M | re.I)

    for match in matches:
        line = match[0]
        name = match[1]
        if "common" in name:
            lib = '%s/%s.lua' % (paths.COMMON_LIB_DIR, name)
        else:
            lib = '%s/%s.lua' % (paths.SUITE_LIB_DIR, name)
        if lib in imports:
            raise RuntimeError(
                'You already start importing %s in %s.'
                % (lib, imports[lib])
            )
        # print('    Importing %s' % (name))
        imports[lib] = filename
        text = __import_file(lib, False)
        code = code.replace(line, text, 1)

    return code


def __add_header(filename, text):
    test_name = os.path.splitext(os.path.basename(filename))[0]
    regex = r'(--- import (.*))'
    p = re.compile(regex)
    header_pos = 0

    # Move header_pos to after any import statements.

    # find the end of the last import statement found
    last_match = None
    for last_match in p.finditer(text):
        pass

    if last_match:
        header_pos = last_match.span()[1] + 1

    header = """
-- Automatically generated header start
oimp.top('%s')
-- Automatically generated header end
""" % test_name

    # splice in the header after imports
    return text[:header_pos] + header + text[header_pos:]


def __add_footer(filename, text):
    test_name = os.path.splitext(os.path.basename(filename))[0]
    footer = """
-- Automatically generated footer start
oimp.bottom('%s')
-- Automatically generated footer end
""" % test_name
    return text + footer


def __import_file(filename, is_top_file):
    with open(filename) as f:
        text = f.read()
        if is_top_file:
            text = __add_header(filename, text)
            text = __add_footer(filename, text)
        text = __load_imports(filename, text)
        return text


def __save_generated(name, text):
    save = '%s/.generated/%s.lua' % (TEMP_DIR, name)
    path = os.path.dirname(save)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(save, 'w+') as f:
        f.write(text)


def __build_code(scenario, versions):
    print '==> Building scenario %s' % scenario
    imports.clear()

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    line = '-- Code generated at %s\n' % now
    filename = '%s/%s.lua' % (paths.SCENARIOS_CODE_DIR, scenario)
    text = __import_file(filename, True)
    text = __process_datastores(text, versions)
    text = line + text
    __save_generated(scenario, text)

    return text


def raw_get(url):
    return requests.get('https://api.loadimpact.com/v2/' + url, auth=(os.environ['LOADIMPACT_API_TOKEN'], ''))


def json_get(url):
    r = raw_get(url)
    return r.json()


def __get_validate_results(validation):
    stream = validation.result_stream()
    results = {}

    # This loop duplicates some result lines, but in any case it gives us some useful info, TODO FIX using offset
    for result in stream:
        if result['offset'] in results:
            continue
        results[result['offset']] = result
        if 'stack_trace' in result:
            print('%s [%s]: %s @ line %s'
                  % (result['offset'], result['timestamp'], result['message'],
                     result['line_number']))
            print('Stack trace:')
            for filename, line, function in result['stack_trace']:
                print('\t%s:%s in %s' % (function, line, filename))
        else:
            print('%s [%s]: %s' % (result['offset'], result['timestamp'], result['message']))
    print("Validation completed with status '%s'"
          % (loadimpact.UserScenarioValidation.status_code_to_text(validation.status)))
    __save_validation_results(validation)


def __save_validation_results(validation):
    ret = raw_get('user-scenario-validations/%s/results' % validation.id)
    save = '%s/scenario_validation_results/validation.%s.json' % (TEMP_DIR, validation.id)
    path = os.path.dirname(save)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(save, 'w+') as f:
        f.write(ret.text)
    print("Wrote validation results to %s" % save)

    pretty_save = '%s/scenario_validation_results/validation.%s.json.pretty.sh' % (TEMP_DIR, validation.id)
    with open(pretty_save, 'w+') as f:
        f.write("more %s | jq . " % save)
    # make pretty file executable
    st = os.stat(pretty_save)
    os.chmod(pretty_save, st.st_mode | stat.S_IEXEC)
    print("Pretty print results with %s" % pretty_save)


def validate(scenario_id):
    user_scenario = liclient.client.get_user_scenario(scenario_id)
    __validate(user_scenario)


def __validate(user_scenario):
    validation = user_scenario.validate()
    print("Starting validation #%d..." % (validation.id,))
    while True:
        print ".",
        try:
            time.sleep(2)  # No results ready first two seconds
            __get_validate_results(validation)
            break
        except ValueError:  # This happens if results are not yet ready
            pass


def update(scenario_id, name):
    user_scenario = liclient.client.get_user_scenario(scenario_id)

    versions = datastore.get_last_data_store_versions()
    code = __build_code(name, versions)
    user_scenario.load_script = code

    new_data_stores = []
    for ds in user_scenario.data_stores:
        new_data_stores.append(ds)

    user_scenario.data_stores = new_data_stores
    user_scenario.update()
    print '    Updated test scenario %i' % scenario_id
    __validate(user_scenario)
    print '    Validated test scenario %i' % scenario_id
