import os
import systools
import time
import program
import tabulate
import paths
import glob
import browser
import yaml

def start(name, description):
    sequence = get(name)
    now = time.strftime('%Y-%m-%d-%H:%M:%S')
    print('==> [%s] Starting sequence %s' % (now, name))
    browser.open()

    programs = sequence['programs']
    for prog in programs:
        total = program.get_total(prog)
        sleep = total + sequence['wait']
        now = time.strftime('%Y-%m-%d-%H:%M:%S')
        print('==> [%s] Starting program %s (will last %i minutes)' % (now, prog, sleep))
        program.start(prog, description)
        systools.easysleep(sleep * 60)

    now = time.strftime('%Y-%m-%d-%H:%M:%S')
    print('==> [%s] Done' % (now))

def get(name):
    with open(paths.SEQUENCE_PATH % (name)) as f:
        return yaml.load(f)['sequence']


def show_sequences():
    cols = ['SEQUENCE', 'PROGRAM', 'TIME']
    rows = []
    names = glob.glob(paths.SEQUENCE_PATH % ('*'))

    for file_name in names:
        name, ext = os.path.splitext(os.path.basename(file_name))

        max = 0
        sequence = get_sequence(name)
        programs = sequence['programs']
        for s in programs:
            total = program.get_total(s)
            max = max + total + sequence['wait']
            rows.append([
                name,
                s,
                total,
            ])
            name = ''
        rows.append(['', '... Waits', sequence['wait']])
        rows.append(['', '... Total' , max - sequence['wait']])
        rows.append(['', '', ''])

    print tabulate.tabulate(rows, headers=cols)

def get_sequence(name):
    with open(paths.SEQUENCE_PATH % (name)) as f:
        return yaml.load(f)['sequence']