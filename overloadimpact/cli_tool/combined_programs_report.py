import os
import report
import program_report
import config_report
import target
import paths

PROGRAM_BASE_DIR = paths.REPORTS_DIR + "/combined_program_runs"

def generate(program_run_ids):
    program_runs = {}
    for program_run_id in program_run_ids:
        program_report.generate_for_completed(program_run_id) # recreate reports
        program_runs[program_run_id] = program_report.get_run_data(program_run_id)

    __create_page(program_runs)

def __create_page(program_runs):
    __prepare(program_runs)
    report_file_path = __report_url(program_runs)
    file = open(report_file_path, 'w') # Trying to create a new file or open one
    file.write(__page_markup(program_runs))
    file.close()
    print("Wrote combined report to:\n" + report_file_path)

def __dir_name(program_runs):
    dir_name = ".".join(program_runs.keys())
    # limit dir name to 100
    return dir_name[:100]

def __report_url(program_runs):
    return __report_path(program_runs) + "/report.html"

def __report_path(program_runs):
    return PROGRAM_BASE_DIR + "/" + __dir_name(program_runs)

def __prepare(program_runs):
    report_path = __report_path(program_runs)
    try:
        os.mkdir(report_path)
    except:
        pass # print "Path exists: " + report_path

def __page_markup(program_runs):
    markup = report.header("Target report", "For all scenarios: actions/s results vs targets", "")
    markup += __program_runs_markup(program_runs)
    markup += __combined_results_markup(program_runs)
    markup += report.footer()
    return markup


def __combined_results_markup(program_runs):
    target_chart_scenarios = __target_chart_scenarios(program_runs) # get the scenarios valid for target charts
    markup = ""
    scenarios_markup = ""
    scenarios_markup += __combined_scenarios_summary_markup(target_chart_scenarios, program_runs)
    for scenario_name in target_chart_scenarios:
        scenarios_markup += __combined_scenario_markup(scenario_name, program_runs)
    markup += report.section("Combined action/s charts for scenarios with targets", scenarios_markup)
    return markup

def __combined_scenarios_summary_markup(targets_chart_scenarios, program_runs):
    __combined_target_chart(targets_chart_scenarios, program_runs)
    return report.chart_markup("all_runs_and_targets", "")

def __scenario_chart_name(scenario_name):
    return scenario_name + ".combined"

def __combined_scenario_markup(scenario_name, program_runs):
    # create a chart for the scenario with targets and one bar for each program_run
    __target_chart(scenario_name, program_runs)
    # create markup
    return report.chart_markup(__scenario_chart_name(scenario_name), "")

def __program_runs_markup(program_runs):
    markup = ""
    # list program_runs with links to them with a short one line summary
    run_list_markup = ""
    for program_run_id in program_runs:
        run_list_markup += report.link_title(program_report.complete_report_url(program_run_id), "Program_run " + program_run_id, __program_run_1line_summary(program_runs[program_run_id]))

    markup += report.section("Program runs", run_list_markup)
    return markup

def __program_run_1line_summary(program_run):
    markup = "<div style=\"margin-top: -20px;\">configs:<br/>"
    for config_name, config in program_run['program']['configs'].iteritems():
        markup += config_name + " (scenarios: "
        scenario_strs = []
        for scenario_name, scenario in config['scenarios'].iteritems():
            scenario_strs.append("%s %.02f%%" % (scenario_name, scenario["percent-of-users"]))
        markup += ", ".join(scenario_strs)
        markup += ("), %d total users <br/>" % (config["users"]))

    return "" + markup + "</div>"
    # return "<pre>" + json.dumps(program_run['program']['configs'], indent=4, separators=(',', ': ')) + "</pre><br/>"

def __target_chart_scenarios(program_runs):
    scenarios = {}
    for program_name, program_run in program_runs.iteritems():
        for config_name, config in program_run['program']['configs'].iteritems():
            for scenario_name, scenario in config['scenarios'].iteritems():
                scenarios[scenario_name] = True
    return scenarios

def __combined_target_chart(target_chart_scenarios, program_runs):
    chart = report.pygal_bar()

    # chart.x_labels = map(str, range(2002, 2013))
    # chart.add('Firefox', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
    # chart.add('Chrome',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])

    sets = {}
    # collect target sets
    for target_name, target_arr in target.get_targets().iteritems():
        target_title = "Target " + target_name
        sets[target_title] = {}
        for scenario_name in target_chart_scenarios:
            sets[target_title][scenario_name] = target_arr[scenario_name]['actions-per-sec']


    for program_run_name, program_run in program_runs.iteritems():
        sets[program_run_name] = {}
        # collect scenario run  for each program sets
        for config_name, config_run in program_run['config_runs'].iteritems():
            config_params = config_run['config_params']
            for scenario_name in config_run['config_params']['scenarios']:
                scenario_params = config_params['scenarios'][scenario_name]
                sets[program_run_name][scenario_name] = config_report.scenario_peak_core_actions_per_sec_avg(scenario_name, config_run['enriched_metrics'], scenario_params)

    chart.title = 'All scenarios: action/s - program comparison'
    # make entries
    data_sets = {}
    x_labels = []
    for set_name, set in sets.iteritems():
        set_title = __format_set_title(set_name)
        data_sets[set_name] = {"title": set_title, "data":[]}

    x_labels = []
    for scenario_name in target_chart_scenarios:
        x_labels.append(scenario_name)
    x_labels = sorted(x_labels)

    # arrange data arrays according to sorted scenario_names
    for scenario_name in x_labels:
        for set_name, _set in sets.iteritems():
            if scenario_name in sets[program_run_name]:
                data_sets[set_name]["data"].append(_set[scenario_name])
            else:
                data_sets[set_name]["data"].append(None)

    chart.x_labels = map(__format_set_title, x_labels)
    # att chart sets for each target and program_run
    sorted_set_names = sorted(data_sets)
    for set_name in sorted_set_names:
        chart.add(data_sets[set_name]["title"], data_sets[set_name]["data"])

    chart.render_to_file(__report_path(program_runs) + "/all_runs_and_targets.svg")

def __format_set_title(key):
 return (key[:25] + '..') if len(key) > 25 else key

def __target_chart(scenario_name, program_runs):
    chart = report.pygal_bar()
    entries = {}

    # get targets
    for target_name, target_arr in target.get_targets().iteritems():
        target_title = "Target " + target_name
        entries[target_title.upper()] = target_arr[scenario_name]['actions-per-sec']

    program_scenarios_processed = {}

    # for each config in each program try to find a matching scenario
    for program_run_name, program_run in program_runs.iteritems():
        program_scenarios_processed[program_run_name] = {}
        for config_name, config_run in program_run['config_runs'].iteritems():
            if scenario_name in program_scenarios_processed[program_run_name]: # already checked for this program
                break
            if scenario_name in config_run['config_params']['scenarios']:
                config_params = config_run['config_params']
                scenario_params = config_params['scenarios'][scenario_name]

                # if we have an empty entry here from previous iterations, then remove it, since we have found a valid one
                if program_run_name in entries:
                    entries.pop(program_run_name, None)
                program_run_title = "%s (%d vu's)" % (program_run_name, int(config_params['users'] * (scenario_params["percent-of-users"] / 100.0)))
                entries[program_run_title] = config_report.scenario_peak_core_actions_per_sec_avg(scenario_name, config_run['enriched_metrics'], scenario_params)
                program_scenarios_processed[program_run_name][scenario_name] = True
            else:
                entries[program_run_name] = None

    chart.title = scenario_name + ': action/s - program comparison'
    sorted_keys = sorted(entries)
    sorted_vals = map(lambda key: entries[key], sorted_keys)
    chart.x_labels = map(__format_set_title, sorted_keys)
    chart.add('Actions/s', sorted_vals)
    chart.render_to_file(__report_path(program_runs) + "/" + __scenario_chart_name(scenario_name) + ".svg")


    # Alternative implementation: Adding targets as separate data sets:

    # # add one data set for each target to visualize targets
    # for target_name, target_arr in target.get_targets().iteritems():
    #     target_title= "Target " + target_name
    #     target_val = target_arr[scenario_name]['actions-per-sec']
    #     chart.add(target_title, [target_val])

    # for program_run_name, program_run in program_runs.iteritems():
    #     for config_name, config_run in program_run['config_runs'].iteritems():
    #         if config_run['config_params']['scenarios'][scenario_name]:
    #             config_params = config_run['config_params']
    #             scenario_params = config_params['scenarios'][scenario_name]
    #             program_run_title = "%s (%d vu's)" % (program_run_name, int(config_params['users'] * (scenario_params["percent-of-users"] / 100.0)))

    #             entries[program_run_title] = config_report.scenario_peak_core_actions_per_sec_avg(scenario_name, config_run['enriched_metrics'])
    #         else:
    #             entries[program_run_name] = None

    # chart.title = scenario_name + ': action/s - across runs'
    # chart.x_labels = entries.keys()
    # chart.add('Actions/s', entries.values())
