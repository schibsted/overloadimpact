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
      oimp report config [ACTION] [RUN_ID] [TITLE]
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

    elif args['config']:
        command.configcmd(args['NAME'])

    elif args['report']:
        if args['program']:
            command.program_reportcmd(args['ACTION'], args['PROGRAM_RUN_ID'])
        elif args['config']:
            command.config_reportcmd(args['ACTION'], args['RUN_ID'], args['TITLE'])
        else:
            exit('You need to pick a report type.')

    elif args['program']:
        command.programcmd(args['NAME'], args['RUN_DESCRIPTION'])

    elif args['scenario']:
        if args['ACTION']:
            command.scenariocmd(args['ACTION'], args['NAME'])
        else:
            exit('You must specify an action and a scenario name. Use oimp scenario validate [name] or oimp scenario update [name].')

    elif args['target']:
        command.targetcmd(args['NAME'])


    elif args['method']:
        command.api_method(args['NAME'], args['ARGS'])

    else:
        exit('This is not the command you are looking for.')
