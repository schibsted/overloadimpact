#!/usr/bin/env python
import paths
import yaml
import liclient
import tabulate
import scenario
import config_report

def get(name):
    with open(paths.PROGRAMS_PATH % (name)) as f:
        return yaml.load(f)['configs']

def start(id):
    test_config = liclient.client.get_test_config(id)
    run_id = test_config.start_test()
    print('==> Started test %s' % (test_config.name))
    # config_report.generate_for_running(run_id, title)
    return run_id

def get_configs():
    with open(paths.CONFIGS_FILE) as f:
        return yaml.load(f)['configs']

def configure(id, users, warmup, stable=0, scenarios=None):
    steps = [{'users': users, 'duration': warmup}]

    if stable:
        steps.append({'users': users, 'duration': stable, })

    test_config = liclient.client.get_test_config(id)
    test_config.url = 'dummy'
    test_config.config['load_schedule'] = steps
    if scenarios:
        test_config.config[u'tracks'] = __configure_tracks(test_config, scenarios)
    test_config.update()

    test_config = liclient.client.get_test_config(id)
    load_schedule = test_config.config['load_schedule']
    print("test_config.py:" + repr(37) + ":test_config:" + repr(test_config))

    print('==> Updated config %s' % (test_config.name))

    for step in load_schedule:
        print('    Duration: %s  Users: %s' % (str(step['duration']).rjust(2), step['users']))

def __configure_tracks(test_config, scenario_params):
    tracks = []

    scenarios = scenario.get_scenarios()

    for scenario_name in scenario_params:
        track = {}
        track[u'loadzone'] = u'amazon:ie:dublin'
        clip = {}
        clip[u'user_scenario_id'] = scenarios[scenario_name]["id"]
        clip[u'percent'] = scenario_params[scenario_name]['percent-of-users']
        track[u'clips'] = [clip]
        tracks.append(track)
    return tracks

def show_configs():
    cols = ['CONFIG', 'ID']
    rows = []
    configs = get_configs()
    for name in configs:
        config = configs[name]
        rows.append([
            name,
            config['id'],
        ])

    print tabulate.tabulate(rows, headers=cols)
