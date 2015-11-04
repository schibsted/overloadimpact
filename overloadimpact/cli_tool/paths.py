import os
import errno

def first_diff_pos(a, b):
    """
    find the pos of first char that doesn't match
    """
    for i, c in enumerate(a):
        if i >= len(b):
            return i # return if reached end of b
        if b[i] != a[i]:
            return i # we have come to the first diff

    return len(a) # we have reached the end of string a

def determine_suite_dir():
    if "OIMP_PROJECT_HOME" in os.environ:
        if os.path.isdir(os.environ["OIMP_PROJECT_HOME"] + "/lua/scenarios"):
            return os.environ["OIMP_PROJECT_HOME"]
    print('OIMP_PROJECT dir not found. Set it as OIMP_PROJECT_HOME env var, or execute from it\'s root dir.\nYou can set up a new project with: oimp setup_project [name] [destination path].')
    return False
    # if we have executed this command from a oimp-suite dir then it will contain /lua/scenarios
    current_path = os.getcwd()
    if os.path.isdir(current_path + "/lua/scenarios"):
        return current_path
    print('OIMP_PROJECT dir not found. Set it as OIMP_PROJECT_HOME env var, or execute from it\'s root dir.\nYou can set up a new project with: oimp setup_project [name] [destination path].')
    return False

def relative_path(from_path, to_path):
    diff_pos = first_diff_pos(from_path, to_path)
    if diff_pos == 0: # no relative path possible
        return to_path
    diff_path = from_path[diff_pos:]
    num_slashes = diff_path.count("/")
    rel_path = ("../" * num_slashes) + to_path[diff_pos:]
    return rel_path

def determine_run_data_dir():
    if "OIMP_PROJECT_RUN_DATA_HOME" in os.environ:
        if os.path.isdir(os.environ["OIMP_PROJECT_RUN_DATA_HOME"] + "/runs"):
            return os.environ["OIMP_PROJECT_RUN_DATA_HOME"] + "/runs"
        print('OIMP_PROJECT_RUN_DATA dir not found. Set it as OIMP_PROJECT_RUN_DATA_HOME env var, or execute from it\'s root dir.\nYou can set up a new project with: oimp setup_project [name] [destination path].')
        return False
    # if we have executed this command from a oimp-suite dir then it will contain /lua/scenarios
    current_path = os.getcwd()
    if os.path.isdir(current_path + "/runs"):
        return current_path + "/runs"
    print('OIMP_PROJECT_RUN_DATA dir not found. Set it as OIMP_PROJECT_RUN_DATA_HOME env var, or execute from it\'s root dir.\nYou can set up a new project with: oimp setup_project [name] [destination path].')
    return False

def determine_run_data_reports_dir():
    if "OIMP_PROJECT_RUN_DATA_HOME" in os.environ:
        if os.path.isdir(os.environ["OIMP_PROJECT_RUN_DATA_HOME"] + "/reports"):
            return os.environ["OIMP_PROJECT_RUN_DATA_HOME"] + "/reports"
        print('OIMP_PROJECT_RUN_DATA dir not found. Set it as OIMP_PROJECT_RUN_DATA_HOME env var, or execute from it\'s root dir.\nYou can set up a new project with: oimp setup_project [name] [destination path].')
        return False
    # if we have executed this command from a oimp-suite dir then it will contain /lua/scenarios
    current_path = os.getcwd()
    if os.path.isdir(current_path + "/reports"):
        return current_path + "/reports"
    print('OIMP_PROJECT_RUN_DATA dir not found. Set it as OIMP_PROJECT_RUN_DATA_HOME env var, or execute from it\'s root dir.\nYou can set up a new project with: oimp setup_project [name] [destination path].')
    return False

def sub_reports_base_dir():
    return REPORTS_DIR + sub_reports_prefix

def program_reports_dir():
    return sub_reports_base_dir() + "/program_runs"
 
def config_reports_dir():
    return sub_reports_base_dir() + "/config_runs"

def combined_program_reports_dir():
    return REPORTS_DIR + "/combined_program_runs"

def runs_dir():
    return RUNS_DIR

def program_runs_dir():
    return runs_dir() + "/program_runs"

def config_runs_dir():
    return runs_dir() + "/config_runs"

sub_reports_prefix = ""
def set_sub_reports_prefix(prefix):
    global sub_reports_prefix
    sub_reports_prefix = "/" + prefix


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def suite_defined():
    return SUITE_DIR

COMMON_LIB_DIR = os.path.dirname(os.path.realpath(__file__)) + "/../lua/lib"
REPORT_TEMPLATES_DIR = os.path.dirname(os.path.abspath(__file__)) + "/reports/templates"

SUITE_DIR = determine_suite_dir()

if SUITE_DIR:
    SCENARIOS_CODE_DIR = SUITE_DIR + "/lua/scenarios"
    SUITE_LIB_DIR = SUITE_DIR + "/lua/lib"

    CONFIGS_FILE   = SUITE_DIR + '/suite_config/configs.yaml'
    SCENARIOS_FILE = SUITE_DIR + '/suite_config/scenarios.yaml'
    TARGETS_FILE   = SUITE_DIR + '/suite_config/targets.yaml'
    PROGRAMS_PATH    = SUITE_DIR + '/suite_config/programs/%s.yaml'
    SEQUENCE_PATH  = SUITE_DIR + '/suite_config/sequences/%s.yaml'

    REPORTS_DIR = determine_run_data_reports_dir()
    RUNS_DIR = determine_run_data_dir()
