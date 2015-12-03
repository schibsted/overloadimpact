#!/usr/bin/env python
import tabulate
import yaml
import paths


def get(name):
    with open(paths.TARGETS_FILE) as f:
        return yaml.load(f)['targets'][name]


def show_targets():
    cols = ['TARGET', 'SCENARIO', 'ACTIONS-PER-SEC']
    rows = []
    targets = get_targets()
    for name in targets:
        print("name:" + repr(name))
        target = targets[name]
        for scenario_name in target:
            rows.append([
                name,
                scenario_name,
                target[scenario_name]['actions-per-sec'],
            ])

    print tabulate.tabulate(rows, headers=cols)


def get_targets():
    with open(paths.TARGETS_FILE) as f:
        return yaml.load(f)['targets']
