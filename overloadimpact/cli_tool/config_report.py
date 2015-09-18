import shutil
import code
import numpy
import operator
import scenario
import time
import os
import json
import sys
import liclient
import loadimpact
import math
import report
import paths

REPORTS_PATH = paths.RUNS_DIR

# Make loadimpact class TestResult available in this scope
TestResult = loadimpact.resources.TestResult

LI_WORLD_REGION_ID = 1
LIVE_FEEDBACK_KEY="__li_live_feedback"
CLIENTS_ACTIVE_KEY="__li_clients_active"
USER_LOAD_TIME_KEY='__li_user_load_time'

def get_enriched_metrics(config_run, title):
    return __enrich_metrics(__get_metrics(config_run, title, False))

def generate_for_completed(config_run, title):
    __generate(config_run, title, False)

def generate_for_running(config_run, title):
    __generate(config_run, title, True)

def __get_stored_metrics(run_id):
    with open(__metrics_json_path(run_id),'r') as f:
        json_str = f.read()
        return json.loads(json_str)

def __get_result_ids(config_run):
    world_id=LI_WORLD_REGION_ID

    test_result_ids = [
        TestResult.result_id_from_name(TestResult.LIVE_FEEDBACK),
        TestResult.result_id_from_name(TestResult.ACTIVE_USERS,
                                       load_zone_id=world_id),
        TestResult.result_id_from_name(TestResult.REQUESTS_PER_SECOND,
                                       load_zone_id=world_id),
        TestResult.result_id_from_name(TestResult.USER_LOAD_TIME,
                                       load_zone_id=world_id)
    ]

    # add scenario specific metrics
    scenarios = config_run["config_params"]["scenarios"]
    for scenario_name in scenarios:
        scenario_id = scenario.get(scenario_name)["id"]
        page_name = __scenario_action_page_name(scenarios[scenario_name])
        test_result_ids.append(TestResult.result_id_for_page(page_name, world_id, scenario_id))
    return test_result_ids

def __get_clients_active(metrics, live_run):
    return metrics[__get_clients_active(live_run)]

def __scenario_action_page_name(scenario_config):
    if "actions-per-sec-page" in scenario_config:
        return scenario_config["actions-per-sec-page"]
    else:
        return "app"

def __get_metrics(config_run, title, live_run=True):
    run_id = config_run["run_id"]

    __prepare(run_id)
    __save_meta(run_id, title, config_run)

    metrics = None
    if live_run:
        print("Current runtime report is " + __report_path(run_id) + "/runtime/runtime_report.html")
        create_runtime_report = True
        test_run = liclient.client.get_test(run_id)
        stream = test_run.result_stream(__get_result_ids(config_run))
        # Wait for test to finish
        for data in stream(poll_rate=3):
            if (CLIENTS_ACTIVE_KEY not in data): # Only treat data which has real metrics, otherwise it is just booting msg etc. (e.g. live feed)
                continue
            metrics = stream.series
            __store_metrics(run_id, metrics)
            if create_runtime_report:
                # update timestamp to trigger js auto-reload
                __update_runtime_timestamp(run_id, report.get_last_timestamp(metrics))
                __runtime_charts(run_id, metrics, config_run)
            time.sleep(3)
        __store_metrics(run_id, metrics)
        metrics = stream.series
    else:
        metrics = __get_finished_run_results(run_id, config_run)
    if (CLIENTS_ACTIVE_KEY not in metrics): # Only treat data which has real metrics, otherwise it is just booting msg etc. (e.g. live feed)
        print("metrics (for config run %s) missing %s, we assume data is incomplete" % (run_id, CLIENTS_ACTIVE_KEY))
        print("submetrics present: " + ", ".join(metrics.keys()))
        return
    clients_active = metrics[CLIENTS_ACTIVE_KEY]
    if not clients_active:
        print("metrics (for config run %s) missing %s, we assume data is incomplete" % (run_id, CLIENTS_ACTIVE_KEY))
        print("submetrics present: " + ", ".join(metrics.keys()))
        return
    return metrics

def __generate(config_run, title, live_run=True):
    run_id = config_run["run_id"]
    print("Generate report for config run_id: " + repr(run_id))
    metrics = __get_metrics(config_run, title, live_run)
    metrics = __enrich_metrics(metrics)
    __complete_charts(run_id, metrics, title, config_run)
    if live_run:
        __update_runtime_timestamp(run_id, report.get_last_timestamp(metrics), "true") # trigger termination runtime report js reload loop
        print("Finished run " + repr(run_id))
    print("Complete report for test_config run " + repr(run_id) + ":\n" + complete_report_url(run_id))

def __get_finished_run_results(run_id, config_run):
    result_ids = __get_result_ids(config_run)
    result_ids_str = "?ids="
    for result_id in result_ids:
        result_ids_str += "" + result_id + ","
    result_ids_str = result_ids_str[0:-1]
    results = code.json_get('tests/%s/results%s' % (run_id, result_ids_str))
    return results

# Add dictionaries indexed by LI offset value
# Add dictionaries indexed by LI timestamp value
# Add sample_period metrics
def __enrich_metrics(metrics):
    metrics = __remove_dups_from_metrics(metrics)
    new_metrics = {}
    for sub_metric_name, sub_metrics in metrics.iteritems():
        if sub_metric_name == LIVE_FEEDBACK_KEY: # do not enrich live feedback data
            continue
        new_metrics[sub_metric_name + '.offset_idx'] = __custom_idx_dict("offset", sub_metrics)
        new_metrics[sub_metric_name + '.timestamp_idx'] = __custom_idx_dict("timestamp", sub_metrics)
    for new_metric_name, new_metric in new_metrics.iteritems():
        metrics[new_metric_name] = new_metric
    metrics['sample_period'] = __find_sample_period(metrics)
    return metrics

def __custom_idx_dict(idx_name, sub_metrics, int_conv=False):
    if int_conv:
        keys = map(lambda metric: int(metric[idx_name]), sub_metrics)
    else:
        keys = map(lambda metric: metric[idx_name], sub_metrics)
    return dict(zip(keys, sub_metrics))

# Should not be necessary but we are getting metric entry duplicates from LI Python SDK
def __remove_dups_from_metrics(metrics):
    metric_dicts = {}
    new_metrics = {}

    # remove dups
    for metric_name, rows in metrics.iteritems():
        metric_dicts[metric_name] = {}
        for row in rows:
            metric_dicts[metric_name][row["offset"]] = row

    # sort by offset
    for metric_name, rows in metric_dicts.iteritems():
        new_metrics[metric_name] = []
        for offset in sorted(rows):
            new_metrics[metric_name].append(rows[offset])

    return new_metrics

def __metrics_json_path(run_id):
    report_path = __report_path(run_id)
    return report_path + "/metrics.json"

def __store_metrics(run_id, metrics):
    json_str = json.dumps(metrics)
    try:
        file = open(__metrics_json_path(run_id), 'w') # Trying to create a new file or open one
        file.write(json_str)
        file.close()
    except:
        print('Something went wrong saving json metrics!')
        sys.exit(0) # quit Python

def __create_report_files(dir):
    shutil.copyfile(paths.REPORT_TEMPLATES_DIR + "/config_runs/runtime_report.html", dir + "/runtime/runtime_report.html")
    shutil.copyfile(paths.REPORT_TEMPLATES_DIR + "/config_runs/timestamp.js", dir + "/runtime/timestamp.js")

def __report_path(run_id):
    return REPORTS_PATH + "/config_runs/" + repr(run_id)

def __meta_json_path(run_id):
    report_path = __report_path(run_id)
    return report_path + "/meta.json"

def  __save_meta(run_id, title, config_run):
    file = open(__meta_json_path(run_id), 'w') # Trying to create a new file or open one
    json_str = json.dumps({"title": title, "config_run": config_run})
    file.write(json_str)
    file.close()

def __get_title(run_id):
    with open(__meta_json_path(run_id), 'r') as f:
        json_str = f.read()
        meta = json.loads(json_str)
        return meta["title"]

def __get_config_run(run_id):
    with open(__meta_json_path(run_id), 'r') as f:
        json_str = f.read()
        meta = json.loads(json_str)
        return meta["config_run"]

def __prepare(run_id):
    report_path = __report_path(run_id)
    try:
        os.mkdir(report_path)
        os.mkdir(report_path + "/runtime")
        os.mkdir(report_path + "/complete")
    except:
        pass # print "Path exists: " + report_path
    __create_report_files(report_path)

def __update_runtime_timestamp(run_id, timestamp, complete="false"):
    report_path = __report_path(run_id)
    try:
        file = open(report_path + "/runtime/timestamp.js", 'w') # Trying to create a new file or open one
        file.write("report_timestamp = " + repr(timestamp) + "; report_done = " + complete + ";")
        file.close()
    except:
        print('Something went wrong updating timestamp!')
        sys.exit(0) # quit Python

def __flows_per_sec(metrics):
    load_times = metrics[USER_LOAD_TIME_KEY]
    client_nums = metrics[CLIENTS_ACTIVE_KEY]

    # match load_time and clients_active by timestamp
    flows_per_sec = {}
    indexed_load_times = {}
    indexed_client_nums = {}
    for load_time in load_times:
        indexed_load_times[load_time['timestamp']] = load_time
    for client_num in client_nums:
        indexed_client_nums[client_num['timestamp']] = client_num

    for timestamp, load_time in indexed_load_times.iteritems():
        if timestamp in indexed_client_nums:
            # We find flows per second by dividing total clients by seconds spent per flow
            active_clients = indexed_client_nums[timestamp]['value']
            load_time_in_sec = load_time['value'] / 1000.0
            flow_per_sec_ratio = round(active_clients / load_time_in_sec, 2)
            flows_per_sec[timestamp] = flow_per_sec_ratio

    return __sort_dict(flows_per_sec)

def __sort_dict(ret):
    sorted_ret = sorted(ret.items(), key=operator.itemgetter(0))
    keys = []
    vals = []
    for entry in sorted_ret:
        keys.append(entry[0])
        vals.append(entry[1])
    return {"keys": keys, "vals": vals}

def __get_metric_as_actions_per_sec(key, metrics, divisor):
    metric_set = metrics[key]
    return map(lambda row: {"timestamp": row["timestamp"], "offset": row["offset"], "avg": round(row["value"] / divisor, 2)}, metric_set)

def __get_metric(key, metrics, divisor):
    metric_set = metrics[key]
    ret = {}
    for data in metric_set:
        ret[data['timestamp']] = round(data['value'] / divisor, 2)
    return __sort_dict(ret)

# Round to nearest whole number
def __round(float_num):
    return int(round(float_num/10, 1) * 10)

# This function will try to get the period from 70% to 90% of the test time, assuming
# that this will give us a sensible average from the max Virtual Users load period.
def __find_sample_period(metrics):
    clients_active = metrics[CLIENTS_ACTIVE_KEY]
    clients_max = 0
    first_max_client_idx = None
    last_max_client_idx = None
    for idx, row in enumerate(clients_active):
        if row['value'] == 0: # should not happen
            continue
        if row['value'] > clients_max: # still scaling up
            clients_max = row['value']
            first_max_client_idx = idx
        elif row['value'] == clients_max: # found the ceiling?
            last_max_client_idx = idx
            continue
        else: # val < clients_max, scaling down again
            # probably scaling down again
            continue
    idx_range = last_max_client_idx - first_max_client_idx
    sample_period_start_idx = __round(first_max_client_idx + math.floor(idx_range * 0.7)) # start from 70% into max_load period
    sample_period_stop_idx = __round(first_max_client_idx + math.floor(idx_range * 0.9)) # stop at 90% into max_load period
    return {"start_row": clients_active[sample_period_start_idx],
            "end_row": clients_active[sample_period_stop_idx]}

def __make_charts(run_id, metrics, dest, config_run):
    flows_per_sec = __flows_per_sec(metrics)
    time_labels = report.make_time_labels(flows_per_sec['keys'])
    active_clients = __get_metric(CLIENTS_ACTIVE_KEY, metrics, 1)
    load_times = __get_metric(USER_LOAD_TIME_KEY, metrics, 1000.0)

    report_path = __report_path(run_id)
    chart = report.pygal_line()
    chart.title = 'Flows per second / active clients'
    chart.x_labels = time_labels
    chart.add('Flows/s', flows_per_sec['vals'])
    chart.add('Active clients', active_clients['vals'], secondary=True)
    chart.render_to_file(report_path + "/" + dest + "/flows_clients.svg")

    report_path = __report_path(run_id)
    chart = report.pygal_line()
    chart.title = 'Flows per second / Avg load time (s)'
    chart.x_labels = time_labels
    chart.add('Flows/s', flows_per_sec['vals'])
    chart.add('Avg load time (s)', load_times['vals'], secondary=True)
    chart.render_to_file(report_path + "/" + dest + "/flows_loadtime.svg")

    report_path = __report_path(run_id)
    chart = report.pygal_line()
    chart.title = 'Flows per second'
    chart.x_labels = time_labels
    chart.add('Flows/s', flows_per_sec['vals'])
    chart.render_to_file(report_path + "/" + dest + "/load.svg")

    time_labels = report.make_time_labels(load_times['keys'])
    chart = report.pygal_line()
    chart.title = 'Avg load time (s)'
    chart.x_labels = time_labels
    chart.add('Avg (s)', load_times['vals'])
    chart.render_to_file(report_path + "/" + dest + "/duration.svg")

    active_clients = __get_metric(CLIENTS_ACTIVE_KEY, metrics, 1)
    time_labels = report.make_time_labels(active_clients['keys'])
    chart = report.pygal_line()
    chart.title = 'Active clients'
    chart.x_labels = time_labels
    chart.add('Active clients', active_clients['vals'])
    chart.render_to_file(report_path + "/" + dest + "/active.svg")

def __page_markup(title, subtitle, config_run, metrics, dest, run_id):
    markup = report.header(title, subtitle, "Scenarios")
    markup += """<div class="scenarios">"""

    scenarios = config_run["config_params"]["scenarios"]
    for scenario_name, scenario_config in scenarios.items():
        markup += __scenario_markup(scenario_name, scenario_config, metrics, dest, run_id)
    markup += """</div>"""

    markup += report.section_title("General results for whole test config", "Normally less useful than scenario stats above because aggregated between different scenarios! Note that flows per second is not adjusted for multiple actions per scenario, so even if a scenario executes 100 actions in one scenario, the whole scenario is calculated as one action.")

    for chart in ["flows_clients", "flows_loadtime", "load", "duration", "active"]:
        markup += report.chart_markup(chart)
    markup += report.footer()
    return markup


def __scenario_app_page_metrics(scenario_name, metrics, scenario_config):
    scenario_id = scenario.get(scenario_name)["id"]
    page_name = __scenario_action_page_name(scenario_config)

    # For legacy tests where "app" page does not wrap the whole test, and where there was only one scenario per
    # test config, we use the whole test config load time instead.
    # An example is has-session which does one login and 100 has-session calls.

    if "use-scenario-load-time" in scenario_config:
        return __get_metric_as_actions_per_sec(USER_LOAD_TIME_KEY, metrics, 1000.0)
    else:
        app_page_metric_id = TestResult.result_id_for_page(page_name, LI_WORLD_REGION_ID, scenario_id)
        return metrics[app_page_metric_id]

def scenario_peak_actions_per_sec(scenario_name, metrics, scenario_config):
    app_page_metrics = __scenario_app_page_metrics(scenario_name, metrics, scenario_config)
    sample_period_metrics = __extract_sample_metrics(app_page_metrics, metrics['sample_period'])
    val_field = "avg"
    return __actions_per_sec(sample_period_metrics, metrics, val_field, scenario_config)

def scenario_peak_actions_per_sec_avg(scenario_name, metrics, scenario_config):
    actions_per_sec = scenario_peak_actions_per_sec(scenario_name, metrics, scenario_config)
    return report.arr_avg(actions_per_sec, "actions_per_sec")

def __scenario_markup(scenario_name, scenario_config, metrics, dest, run_id):
    markup = ""

    # add summary line here with core results for scenario, create and show scenario chart
    peak_actions_per_sec = scenario_peak_actions_per_sec(scenario_name, metrics, scenario_config)
    peak_actions_per_sec_avg = report.arr_avg(peak_actions_per_sec, "actions_per_sec")

    setup_duration_warning = ""
    if "actions-per-scenario" in scenario_config:
        setup_duration_warning = " (Executes %d actions per scenario, the setup time is divided by %d and added to each action duration)" % (scenario_config["actions-per-scenario"], scenario_config["actions-per-scenario"])

    peak_active_clients = map(lambda row: int(row["clients_active"] * (scenario_config['percent-of-users'] / 100.0)), peak_actions_per_sec) # multiply by the fraction of users reserved for this scenario
    # get peak users avg
    peak_clients_avg = int(numpy.mean(peak_active_clients))

    # Get whole test period chart for actions/s
    app_page_metrics = __scenario_app_page_metrics(scenario_name, metrics, scenario_config)
    actions_per_sec = __actions_per_sec(app_page_metrics, metrics, "avg", scenario_config)
    chart_name = scenario_name + ".actions_per_sec"
    chart_title = scenario_name + ': actions/s' + (" (peak avg: %.02f actions/s, users: %d)" % (peak_actions_per_sec_avg, peak_clients_avg))
    active_clients = map(lambda row: int(row["clients_active"] * (scenario_config['percent-of-users'] / 100.0)), actions_per_sec) # multiply by the fraction of users reserved for this scenario
    report.make_time_chart(__report_path(run_id), metrics, chart_title, chart_name, run_id, "Actions/s", actions_per_sec, "actions_per_sec", dest, True, active_clients)

    markup += ("""<div>
    <h3 style="font-weight: lighter">Actions/s for scenario: <span style="font-weight: bold">%s</span>, """ % scenario_name)
    markup += ("""Peak period average <span style="font-weight: bold">actions/s: %.02f</span> </p>""" % peak_actions_per_sec_avg)
    markup += """<p style="font-size: 0.8em">""" + setup_duration_warning + """</p>"""
    markup += report.chart_markup(chart_name)
    markup += "</div>"


    # peak period action/s chart
    chart_name = scenario_name + ".actions_per_sec.peak_period"
    chart_title = scenario_name + ': peak traffic actions/s' + (" (avg: %.02f, users: %d)" % (peak_actions_per_sec_avg, peak_clients_avg))
    report.make_time_chart(__report_path(run_id), metrics, chart_title, chart_name, run_id, "Actions/s", peak_actions_per_sec, "actions_per_sec", dest, False, None)

    markup += ("""<div>
    <h3 style="font-weight: lighter">Actions/s on peak load for scenario: <span style="font-weight: bold">%s</span>, """ % scenario_name)
    markup += ("""Peak period average <span style="font-weight: bold">actions/s: %.02f</span> </p>""" % peak_actions_per_sec_avg)
    markup += """<p style="font-size: 0.8em">""" + setup_duration_warning + """</p>"""
    markup += report.chart_markup(chart_name)
    markup += "</div>"


    # Get whole test period chart for avg duration
    chart_name = scenario_name + ".avg_durations"
    chart_title = scenario_name + ': avg duration' + (" (users: %d)" % (peak_clients_avg))
    report.make_time_chart(__report_path(run_id), metrics, chart_title, chart_name, run_id, "Avg duration (s)", app_page_metrics, "avg", dest, True, active_clients)

    markup += ("""<div>
    <h3 style="font-weight: lighter">Avg duration for scenario: <span style="font-weight: bold">%s</span>, """ % scenario_name)
    markup += ("""Peak period average <span style="font-weight: bold">actions/s: %.02f</span> </p>""" % peak_actions_per_sec_avg)
    markup += """<p style="font-size: 0.8em">""" + setup_duration_warning + """</p>"""
    markup += report.chart_markup(chart_name)
    markup += "</div>"

    return markup

def __runtime_charts(run_id, metrics, config_run):
    __make_charts(run_id, metrics, "runtime", config_run)

def __get_timestamp_closest_value(ts_indexed_rows, needle_ts, value_name="value"):
    closest_ts = needle_ts
    closest_ts_val = ts_indexed_rows[closest_ts][value_name]
    return closest_ts_val

    # didn't get bisect to work correctly but in any case it should not be necessary because all timestamps seem to be present in li_clients_active
    # keys = ts_indexed_rows.keys()
    # closest_ts = __find_le(keys, needle_ts)
    # return closest_ts_val

# def __find_le(l, x):
#     'Find rightmost value less than or equal to x in list a'
#     pos = bisect.bisect(l, x)
#     if l[pos + 1] == x: # exact value exists
#         return x
#     return l[pos]

# Get the active_clients value closest to the timestamp of the row
def __clients_active_for_row(row, metrics):
    row_timestamp = row["timestamp"]
    closest_clients_active = __get_timestamp_closest_value(metrics[CLIENTS_ACTIVE_KEY + ".timestamp_idx"], row_timestamp)
    return closest_clients_active

def __actions_per_sec(sub_metrics, metrics, val_key, scenario_config):
    ret = []
    for row in sub_metrics:
        clients_active = __clients_active_for_row(row, metrics)
        scenario_duration = float(row[val_key])

        # Some scenarios, like has-session, executes multiple has-session per scenario run.
        #
        # If we execute 100 actions per scenario, we must divide load time by 100.
        # Note that we need to divide the WHOLE scenario load time, also including whatever time
        # spent setting up the test (e.g. getting a login session, before running has-session).
        # This, because we are interested in how many actions were ACTUALLY ran in the time period. If we exclude
        # the setup time, then the actions-per-sec calculation is wrong, and would not match real numbers.
        #
        # Example:
        # Setup time 1s, 10 actions taking 0.3s each. 100 Virtual users.
        # 100 / (1 + 3)s = 25 scenario executions per sec. Each scenario is 10 actions, so 250 actions per sec.
        #
        # If we exclude the setup time we would erroneously get:
        # 100 / 3s = 33.3 scenario executions per sec, which was not what actually happened, and we would
        # get 333 actions per sec, which is wrong.
        action_duration = None
        if "actions-per-scenario" in scenario_config:
            action_duration = scenario_duration / scenario_config["actions-per-scenario"]
        else:
            action_duration = scenario_duration
        ret.append({
            "timestamp": row["timestamp"],
            "offset": row["offset"],
            "clients_active": clients_active,
            "actions_per_sec": float(clients_active) / action_duration # actions/sec is virtual_users/duration
        })
    return ret

# extract data from the sample period
def __extract_sample_metrics(sub_metrics, sample_period):
    start_idx = None
    end_idx = None
    for idx, row in enumerate(sub_metrics):
        if row["timestamp"] < sample_period["start_row"]["timestamp"]: # before sample period
            continue
        elif row["timestamp"] == sample_period["end_row"]["timestamp"]: # found row matching end_row timestamp, use as end_idx
            end_idx = idx
            break
        elif row["timestamp"] > sample_period["end_row"]["timestamp"]: # found row surpassing end_row timestamp, return previous row
            end_idx = idx - 1
            break
        elif row["timestamp"] >= sample_period["start_row"]["timestamp"]: # found first row >= start_row timestamp, use as start_idx
            if not start_idx:
                start_idx = idx
    return sub_metrics[start_idx:end_idx]

def __complete_charts(run_id, metrics, title, config_run):
    if title == None:
        title = ""

    subtitle = "Run " + repr(run_id) + ", " + report.get_start_time(metrics)
    __make_charts(run_id, metrics, "complete", config_run)

    file = open(complete_report_url(run_id), 'w') # Trying to create a new file or open one
    file.write(__page_markup(title, subtitle, config_run, metrics, "complete", run_id))
    file.close()

def complete_report_url(run_id):
    report_path = __report_path(run_id)
    return report_path + "/complete/complete_report.html"


