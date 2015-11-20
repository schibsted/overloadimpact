#!/usr/bin/env python
import paths
import re

def sequencecmd(name, run_description):
    if not paths.suite_defined(): return # cannot run without project env defined
    import sequence
    if name:
        if not run_description:
            print("Add a second argument to describe the program execution, e.g.: '40 web fronts, Redis backend'")
        else:
            sequence.start(name, run_description)
    else:
        sequence.show_sequences()

def programcmd(name, run_description):
    if not paths.suite_defined(): return # cannot run without project env defined
    import program
    if name:
        if not run_description:
            print("Add a second argument to describe the program execution, e.g.: '40 web fronts, Redis backend'")
        else:
            program.start(name, run_description)
    else:
        program.show_programs()

def scenariocmd(action, name):
    if not paths.suite_defined(): return # cannot run without project env defined
    import scenario
    if action == "validate":
        if name:
            scenario.validate(name)
        else:
            scenario.show_scenarios()
    elif action == "update":
        scenario.update(name)
    else:
        print("""To validate scenario:
oimp scenario validate [scenario_name]

To update all scenarios:

oimp scenario update

To update a scenario:

oimp scenario update [name]""")

def targetcmd():
    if not paths.suite_defined(): return # cannot run without project env defined
    import target
    target.show_targets()

def test_configcmd(name):
    if not paths.suite_defined(): return # cannot run without project env defined
    import test_config
    if name:
        configs = test_config.get_configs()
        config  = configs[name]
        run_id  = test_config.start(config['id'])
        # config_report.start_report(run_id, name) # disabled dynamic reporting for now
    else:
        test_config.show_configs()

def program_reportcmd(action, program_run_id):
    if not paths.suite_defined(): return # cannot run without project env defined
    import program_report
    import combined_programs_report
    if action == "running":
        program_report.generate_for_running(program_run_id)
    elif action == "completed":
        program_report.generate_for_completed(program_run_id)
    elif action == "combine":
        combined_programs_report.generate(program_run_id.split(','))
    else:
        program_report.list_runs()
        print("Generate the report with: oimp report program [running/completed/combine] [program_run_name(s)]")

def test_config_reportcmd(action, run_id, title):
    if not paths.suite_defined(): return # cannot run without project env defined
    import config_report
    if action == "running":
        config_report.generate_for_running_by_id(run_id, title)
    if action == "completed":
        config_report.generate_for_completed_by_id(run_id, title)
    else:
        config_report.list_runs()
        print("Generate the report with: oimp report config [running/completed] [program_run_name]")

def api_methodcmd(name, args):
    if not paths.suite_defined(): return # cannot run without project env defined
    import api_method
    if name:
        api_method.run_method(name, args)
    else:
        api_method.show_methods()

def setup_project_reportcmd(name, dest_dir):
    import project
    project.setup(re.sub(r'\W+', '', name), dest_dir)

