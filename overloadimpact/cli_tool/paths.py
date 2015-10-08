import os

def determine_suite_dir():
    if "OIMP_SUITE_HOME" in os.environ:
        if os.path.isdir(os.environ["OIMP_SUITE_HOME"] + "/lua/scenarios"):
            return os.environ["OIMP_SUITE_HOME"]
        raise NameError('OIMP_SUITE dir not found. Set it as OIMP_SUITE_HOME env var, or execute from it\'s root dir.')
    # if we have executed this command from a oimp-suite dir then it will contain /lua/scenarios
    current_path = os.getcwd()
    if os.path.isdir(current_path + "/lua/scenarios"):
        return current_path
    raise NameError('OIMP_SUITE dir not found. Set it as OIMP_SUITE_HOME env var, or execute from it\'s root dir.')

def determine_run_data_dir():
    if "OIMP_SUITE_RUN_DATA_HOME" in os.environ:
        if os.path.isdir(os.environ["OIMP_SUITE_RUN_DATA_HOME"] + "/runs"):
            return os.environ["OIMP_SUITE_RUN_DATA_HOME"] + "/runs"
        raise NameError('OIMP_SUITE_RUN_DATA dir not found. Set it as OIMP_SUITE_RUN_DATA_HOME env var, or execute from it\'s root dir.')
    # if we have executed this command from a oimp-suite dir then it will contain /lua/scenarios
    current_path = os.getcwd()
    if os.path.isdir(current_path + "/runs"):
        return current_path + "/runs"
    raise NameError('OIMP_SUITE_RUN_DATA dir not found. Set it as OIMP_SUITE_RUN_DATA_HOME env var, or execute from it\'s root dir.')

SUITE_DIR = determine_suite_dir()

SCENARIOS_CODE_DIR = SUITE_DIR + "/lua/scenarios"
SUITE_LIB_DIR = SUITE_DIR + "/lua/lib"
COMMON_LIB_DIR = os.path.dirname(os.path.realpath(__file__)) + "../lua/lib"
# COMMON_LIB_DIR = os.path.abspath(BASE_DIR + '/../lua/lib')

CONFIGS_FILE   = SUITE_DIR + '/suite_config/configs.yaml'
SCENARIOS_FILE = SUITE_DIR + '/suite_config/scenarios.yaml'
TARGETS_FILE   = SUITE_DIR + '/suite_config/targets.yaml'
PROGRAMS_PATH    = SUITE_DIR + '/suite_config/programs/%s.yaml'
SEQUENCE_PATH  = SUITE_DIR + '/suite_config/sequences/%s.yaml'

RUNS_DIR = determine_run_data_dir()

REPORT_TEMPLATES_DIR = os.path.abspath(__file__) + "/reports/templates"
