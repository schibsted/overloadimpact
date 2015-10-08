#!/usr/bin/env python
import program
import program_report
import config_report
import combined_programs_report
import scenario
import project
import target
import sequence
import test_config
import api_method
import re

def sequencecmd(name, run_description):
    if name:
        if not run_description:
            print("Need a run_description to identify program execution, e.g.: '40 web fronts, Redis backend'")
        else:
            program.start(name, run_description)
    else:
        sequence.show_sequences()

def programcmd(name, run_description):
    if name:
        if not run_description:
            print("Need a run_description to identify program execution, e.g.: '40 web fronts, Redis backend'")
        else:
            program.start(name, run_description)
    else:
        program.show_programs()

def scenariocmd(action, name):
    if action == "validate":
        if name:
            scenario.validate(name)
        else:
            scenario.show_scenarios()
    elif action == "update":
        scenario.update_some(name)
    else:
        print("""To run scenario:
oimp scenario run [scenario_name]

To update all scenarios:

oimp scenario update

To update a scenario:

oimp scenario update [name]""")

def targetcmd():
    target.show_targets()

def testconfigcmd(name):
    if name:
        configs = test_config.get_configs()
        config  = configs[name]
        run_id  = test_config.start(config['id'])
        # config_report.start_report(run_id, name)
    else:
        test_config.show_configs()

def program_reportcmd(action, program_run_id):
    if action == "running":
        program_report.generate_for_running(program_run_id)
    elif action == "completed":
        program_report.generate_for_completed(program_run_id)
    elif action == "combine":
        combined_programs_report.generate(program_run_id.split(','))
    else:
        print("Generate the report with: oimp report program [running/completed/combine] [program_run_name(s)]")
        program_report.list_runs()

def config_reportcmd(action, run_id, title):
    if action == "running":
        config_report.generate_for_running(run_id, title)
    if action == "completed":
        config_report.generate_for_completed(run_id, title)
    else:
        print("Generate the report with: oimp report config [running/completed] [program_run_name]")
        config_report.list_runs()

def api_methodcmd(name, args):
    if name:
        api_method.run_method(name, args)
    else:
        api_method.show_methods()

def setup_project_reportcmd(name, dest_dir):
    project.setup(re.sub(r'\W+', '', name), dest_dir)

