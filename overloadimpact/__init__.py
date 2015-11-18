# -*- coding: utf-8 -*-


"""
Overloadimpact Test framework
~~~~~~~~~~~~~~~~~~~~~~~

Overloadimpact is a framework for writing and running tests suites for
loadimpact.com. It interacts with the Loadimpact API, and enables report
generation, also across test suite runs.

:copyright: (c) 2015 by Schibsted Products and Technology.
:license: MIT, see LICENSE for more details.

"""

__title__ = 'requests'
__version__ = '0.0.4'
__build__ = 0x000004
__author__ = 'Pål de Vibe, Pedro Barbosa'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Schibsted Products and Technology'

import os
import sys

import docopt

def main():
    BASE_DIR = os.path.abspath(__file__) + "/cli_tool"
    sys.path.append(BASE_DIR)
    from cli_tool import command

    desc = """
    DESCRIPTION:
      Controls loadimpact tests

    USAGE:
      oimp setup_project         [NAME] [DEST_DIR]
      oimp sequence         [NAME] [RUN_DESCRIPTION]
      oimp program         [NAME] [RUN_DESCRIPTION]
      oimp test_config        [NAME]
      oimp scenario      [ ACTION] [NAME]
      oimp report program  [ACTION] [PROGRAM_RUN_ID]
      oimp report test_config [ACTION] [RUN_ID] [TITLE]
      oimp target
      oimp api_method        [NAME] [ARGS ...]
      oimp help
    """

    try:
        args = docopt.docopt(desc)
    except Exception, e:
        print(e)
        exit(1)


    # elif args['show']:
    #   source = args['<source>']
    #   if source:
    #     command.inspect(source)
    #   else:
    #     command.show()

    if args['setup_project']:
        if args['NAME'] and args['DEST_DIR']:
            command.setup_project_reportcmd(args['NAME'], args['DEST_DIR'])
        else:
            exit('You must specify a project name and a destination directory.')

    elif args['sequence']:
        command.sequencecmd(args['NAME'], args['RUN_DESCRIPTION'])

    elif args['report']:
        if args['program']:
            command.program_reportcmd(args['ACTION'], args['PROGRAM_RUN_ID'])
        elif args['test_config']:
            if not args['TITLE']:
                title = "No title"
            else:
                title = args['TITLE']
            command.test_config_reportcmd(args['ACTION'], args['RUN_ID'], title)
        else:
            exit('You need to pick a report type.')

    elif args['test_config']:
        command.test_configcmd(args['NAME'])

    elif args['program']:
        command.programcmd(args['NAME'], args['RUN_DESCRIPTION'])

    elif args['scenario']:
        if args['ACTION']:
            command.scenariocmd(args['ACTION'], args['NAME'])
        else:
            exit('You must specify an action and a scenario name. Use oimp scenario validate [name] or oimp scenario update [name].')

    elif args['target']:
        command.targetcmd()

    elif args['api_method']:
        command.api_methodcmd(args['NAME'], args['ARGS'])

    elif args['help']:
        helpstr = """
See git root README.md for more information.

USAGE:
  project:
      oimp setup_project [NAME] [DEST_DIR]

  scenario:
      oimp scenario update [NAME]
      oimp scenario validate [NAME]

  test_config:
      A test_config is a set of one or more scenarios to be executed together.

      oimp test_config
            List all defined test_configs defined in your_oimp_suite_dir/suite_config/scenarios.yaml
      oimp test_config [NAME]
            Execute test config [NAME]

  program:
      A program is a set of test_configs to be executed together. LoadImpact normally limits us to three
      simultaneous test_configs running. On running a program the test_configs will be reconfigured according
      scenarios listed under each config setting in the program.

      oimp program
            List the names of all defined programs defined in your_oimp_suite_dir/suite_config/programs
      oimp program [NAME] [RUN_DESCRIPTION]
            Execute the program [NAME]
            NAME - The name of the program definition file to be executed.
            RUN_DESCRIPTION - Something like "20 web fronts, Redis DB". Mandatory description of setup.

  sequence:
      A sequence is a sequence of programs to be executed one after another.

      oimp sequence
            List the names of all defined sequences defined in your_oimp_suite_dir/suite_config/sequences
      oimp sequence [NAME] [RUN_DESCRIPTION]
            Execute the sequence [NAME]
            NAME - The name of the sequence definition file to be executed.
            RUN_DESCRIPTION - Something like "20 web fronts, Redis DB". Mandatory description of setup.

  report:
      Reports are html reports with svg charts displaying the results of runs.

      oimp report program
            List the PROGRAM_RUN_ID for all program executions.
      oimp report program completed [PROGRAM_RUN_ID]
            Create a report for a completed program run.
      oimp report program running [PROGRAM_RUN_ID]
            Create a dynamically updating report for a program run currently being executed.
      oimp report program combine [PROGRAM_RUN_ID,PROGRAM_RUN_ID,...]
            Create a combined comparative report for a set of completed program runs.
      oimp report test_config
            List the RUN_ID for all test_config executions.
      oimp report test_config completed [RUN_ID] [TITLE]
            Create a report for a completed test_config run.
            TITLE - optional title for report.
      oimp report test_config running [RUN_ID] [TITLE]
            Create a dynamically updating report for a test_config run currently being executed.
            TITLE - optional title for report.

  targets:
      Targets are a set of load targets (requests/s goals) defined in your_oimp_suite_dir/suite_config/targets.yml.
      They are used in reports to compare actual numbers with what we aim at reaching.

      oimp target
            List targets

  api_method:
      api_method allows custom calls to the LoadImpact API endpoints.

      oimp api_method [NAME] [ARGS ...]
"""
        print helpstr
    else:
        exit('This is not the command you are looking for.')
