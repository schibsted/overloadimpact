#!/usr/bin/env python
import tabulate
import yaml
import paths

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