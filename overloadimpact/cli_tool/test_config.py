#!/usr/bin/env python
import paths
import yaml
import liclient
import tabulate
import scenario
import math

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

def configure(id, users, warmup, stable=0, scenarios=None, source_ip_multiplier=None):
    steps = [{'users': users, 'duration': warmup}]

    if stable:
        steps.append({'users': users, 'duration': stable, })

    test_config = liclient.client.get_test_config(id)
    test_config.url = 'dummy'
    test_config.config['load_schedule'] = steps
    if scenarios:
        test_config.config[u'tracks'] = __configure_tracks(test_config, scenarios)
    # specify source ips
    if not source_ip_multiplier or source_ip_multiplier < 2:
        source_ips = 0
    else:
        # source_ips run from 0-5 (representing 1x,2x,3x,4x,5x or 6x as IP source multiplier)
        # it is multiplied by ceil(vus / 500). Examples:
        # 501 vus with 2x multiplier => source_ips: 2
        # 1 vus with 2x multiplier => source_ips: 1
        # 1 vus with 1x multiplier => source_ips: 0
        # 501 vus with 6x multiplier => source_ips: 10
        # 1000 vus with 6x multiplier => source_ips: 10
        # 1001 vus with 6x multiplier => source_ips: 15

        # With one scenario:
        #                    1x    2x     3x
        # 0-500           0      1      2
        # 501-1000     0      2      4
        # 1001-1500   0      3      6
        # 1501-2000   0      4      8
        # 2001-3000   0      6     12
        # 3001-3500   0      7     14
        # 3501-4000   0      8     16
        # 4001-4500   0      9     18
        # 4501-5000   0    10     20

        # With two scenarios:
        #
        # There is a deviation on 1001-1500, not sure why
        #                    1x    2x     3x
        # 0-500           0      1      2
        # 501-1000     0      2      4
        # 1001-1500   0      4      8
        # 1501-2000   0      4      8
        # 2001-3000   0      6     12
        # 3001-3500   0      7     14
        # 3501-4000   0      8     16
        # 4001-4500   0      9     18
        # 4501-5000   0    10     20
        source_ips = int(math.ceil(users / 500.0)) * (source_ip_multiplier - 1)
    test_config.config[u'source_ips'] = source_ips
    print("test_config.config:" + repr(test_config.config))

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
        total_percent = scenario_params[scenario_name]['percent-of-users']
        if 'multi_regions' in scenario_params[scenario_name]:
            region_percents = __distribute_percents(total_percent, ('use_alternative_regions' in scenario_params[scenario_name]))
        else:
            region_percents = {u'amazon:ie:dublin': total_percent}

        for region in region_percents:
            track = {}
            # track[u'loadzone'] = u'amazon:ie:dublin'
            track[u'loadzone'] = region
            clip = {}
            clip[u'user_scenario_id'] = scenarios[scenario_name]['id']
            clip[u'percent'] = region_percents[region]
            track[u'clips'] = [clip]
            tracks.append(track)
    return tracks

def __distribute_percents(total_percent, alternative_regions):
    if alternative_regions:
        possible_regions = [u"amazon:sg:singapore", u"amazon:au:sydney", u"amazon:jp:tokyo"]
    else:
        possible_regions = [u"amazon:ie:dublin", u"amazon:us:ashburn", u"amazon:us:portland", u"amazon:us:palo alto"]
    if total_percent < 4: # too low to need distribution
        return {possible_regions[0]: total_percent}

    total_regions = len(possible_regions)
    left = total_percent
    slice = int(math.ceil(total_percent / float(total_regions)))
    region_percents = {}
    for region_name in possible_regions:
        current_slice = slice
        if (left - slice) < 0:
            current_slice = left
        left = left - current_slice
        region_percents[region_name] = current_slice
    if left != 0:
        raise ValueError("left is not 0 but %d" % (left))
    return region_percents

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
