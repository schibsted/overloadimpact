#!/usr/bin/env python
import test_config
import tabulate
import os
import re
import json
import datetime
import paths
import yaml
import glob

REPORTS_PATH  = paths.RUNS_DIR
PROGRAM_BASE_DIR = paths.RUNS_DIR + "/program_runs"


def get(name):
    with open(paths.PROGRAMS_PATH % (name)) as f:
        return yaml.load(f)

def start(program_name, run_description):
    program = get(program_name)
    __configure(program)
    configs = test_config.get_configs()

    config_runs = {}

    for config_name in program["configs"]:
        config_params = program["configs"][config_name]
        config = configs[config_name]
        run_id = test_config.start(config['id'])
        config_runs[config_name] = {
            'config_params'      : config_params,
            'config'    : config,
            'run_id'    : run_id,
        }

    # save run data
    __save_program_run(program_name, program, run_description, config_runs)

def __configure(program):
    test_configs = test_config.get_configs()

    for config_name, config_params in program["configs"].iteritems():
        config = test_configs[config_name]
        test_config.configure(config['id'],
                              config_params['users'],
                              config_params['warmup'],
                              config_params.get('stable', 0),
                              config_params['scenarios'],
                              config_params.get('source-ip-multiplier', None))

def show_programs():
    cols = ['PROGRAM', 'CONFIG', 'USERS', 'WARMUP', 'STABLE', 'SCENARIO', 'USER-PORTION']
    rows = []
    names = glob.glob(paths.PROGRAMS_PATH % ('*'))

    for program in names:
        name, ext = os.path.splitext(os.path.basename(program))
        rows.append([name, '', '', '', '', '', ''])

        program = get(name)
        for config_name, config in program["configs"].iteritems():
            rows.append(['', config_name, config['users'], config['warmup'], config['stable'], '', ''])
            for scenario_name in config['scenarios']:
                scenario = config['scenarios'][scenario_name]
                users_percent = scenario['percent-of-users']
                users_percent_str = str(users_percent) + "%"
                if users_percent < 10:
                    users_percent_str = "_" + users_percent_str
                rows.append(['', '', '', '', '', scenario_name, users_percent_str])
            name = ''
        rows.append(['', '', '', '', '', '', ''])

    print tabulate.tabulate(rows, headers=cols)

def __save_program_run(name, program, run_description, config_runs):
    path = __program_run_path(name, run_description)
    os.mkdir(path)
    json_str = json.dumps({"name": name, "program": program, "run_description": run_description, "config_runs": config_runs})
    file = open(path + "/program_run.json", 'w') # Trying to create a new file or open one
    file.write(json_str)
    file.close()

def __program_run_path(name, run_description):
    run_description_path_str = re.sub('[\W]', '', run_description.replace(' ', '_').lower()) # only alphanum and _
    return PROGRAM_BASE_DIR + "/" + name + "." + run_description_path_str + "." + datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

def get_total(program_id):
    program = get(program_id)
    max = 0
    for config_name, config_params in program["configs"].iteritems():
        both = config_params['warmup'] + config_params['stable']
        if both > max:
            max = both

    return max

