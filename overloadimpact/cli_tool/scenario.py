#!/usr/bin/env python
import tabulate
import yaml
import paths
import code

def update(name):
    scenarios = get_scenarios()

    if name:
        names = (name,)
    else:
        print('Are you sure you want to update all these test scenarios?')
        print('- ' + '\n- '.join([x for x in scenarios]))
        print 'Press Ctrl+C to cancel',
        try:
            raw_input()
        except KeyboardInterrupt:
            print("\n")
            exit(1)

        names = scenarios.keys()

    for name in names:
        config = scenarios[name]
        code.update(config['id'], name)


def get(name):
    with open(paths.SCENARIOS_FILE) as f:
        return yaml.load(f)['scenarios'][name]

def show_scenarios():
    cols = ['SCENARIO', 'ID']
    rows = []
    scenarios = get_scenarios()
    for name in scenarios:
        scenario = scenarios[name]
        rows.append([
            name,
            scenario['id'],
        ])

    print tabulate.tabulate(rows, headers=cols)

def get_scenarios():
    with open(paths.SCENARIOS_FILE) as f:
        return yaml.load(f)['scenarios']
