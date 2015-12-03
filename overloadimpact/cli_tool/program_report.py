import config_report
import os
import report
import json
import paths


def __read_program_run(program_run_id):
    filepath = paths.program_runs_dir() + "/" + program_run_id + "/program_run.json"
    with open(filepath) as data_file:
        return json.load(data_file)


def __report_path(program_run_id):
    return "%s/%s" % (paths.program_reports_dir(), program_run_id)


def __prepare(program_run_id):
    report_path = __report_path(program_run_id)
    try:
        paths.mkdir_p(report_path)
    except:
        pass  # print "Path exists: " + report_path

    try:
        os.mkdir(report_path + "/complete")
    except:
        pass  # print "Path exists: " + report_path


def __program_config_run_name(config_run_name, program_run_id):
    return config_run_name + " (program: " + program_run_id + ")"


def get_run_data(program_run_id):
    program_run = __read_program_run(program_run_id)
    # for each config_run_id get metrics via API
    config_runs = program_run['config_runs']
    for config_run_name, config_run in config_runs.items():
        program_run['config_runs'][config_run_name]["enriched_metrics"] = config_report.get_enriched_metrics(
            config_run, __program_config_run_name(config_run_name, program_run_id))

    return program_run


def generate_for_completed(program_run_id):
    __generate(program_run_id, False)


# This can be called right after launching the test because it waits for finished runs
def generate_for_running(program_run_id):
    __generate(program_run_id, True)


def __generate(program_run_id, live_run):
    __prepare(program_run_id)
    # get program_run.json for this program
    program_run = __read_program_run(program_run_id)
    # for each config_run_id get metrics via API
    config_runs = program_run['config_runs']
    for config_run_name, config_run in config_runs.items():
        if live_run:
            config_report.generate_for_running(config_run, __program_config_run_name(config_run_name, program_run_id))
        else:
            config_report.generate_for_completed(config_run, __program_config_run_name(config_run_name, program_run_id))
    f = open(complete_report_url(program_run_id), 'w')  # Trying to create a new file or open one
    f.write(__page_markup(program_run_id, program_run))
    f.close()
    print("Complete report for program:\n" + complete_report_url(program_run_id))


def list_runs():
    onlydirs = [d for d in os.listdir(paths.program_runs_dir()) if
                os.path.isdir(os.path.join(paths.program_runs_dir(), d))]
    mtime = lambda d: os.stat(os.path.join(paths.program_runs_dir(), d)).st_mtime
    sorted_dirs = list(sorted(onlydirs, key=mtime))
    for run_dir in sorted_dirs:
        print(run_dir)


def __page_markup(program_run_id, program_run):
    title = "Program report for %s" % program_run_id
    subtitle = program_run["run_description"]
    markup = report.header(title, subtitle, "Test config run reports (sets of scenario runs)")

    # add links to all test config reports
    run_list_markup = """<div class="config_runs">"""
    config_runs = program_run['config_runs']
    for config_run_name, config_run in config_runs.items():
        config_run_id = config_run["run_id"]
        link_title = "Config run (%s) %s" % (config_run_id, config_run_name)
        run_list_markup += report.link_title(
            paths.relative_path(complete_report_url(program_run_id), config_report.complete_report_url(config_run_id)),
            link_title, __config_run_1line_summary(config_run)) + "<br/>"
    run_list_markup += """</div>"""
    markup += run_list_markup

    markup += report.footer()
    return markup


def __config_run_1line_summary(config_run):
    markup = repr(config_run)
    return markup


def complete_report_url(program_run_id):
    report_path = __report_path(program_run_id)
    return report_path + "/complete/complete_report.html"
