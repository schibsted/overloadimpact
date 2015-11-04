import os

def setup(name, dest_dir):
    if not os.path.isdir(dest_dir):
        print("Please supply a valid destination dir")
        return

    defaults_base_path = os.path.dirname(os.path.realpath(__file__)) + "/../default_suite_dirs"
    suite_dir = os.path.abspath("%s/%s_oimp_suite" % (dest_dir, name))
    suite_run_data_dir = os.path.abspath("%s/%s_oimp_suite_run_data" % (dest_dir, name))
    os.system("cp -rf %s/oimp_suite %s" % (defaults_base_path, suite_dir))
    os.system("cp -rf %s/oimp_suite_run_data %s" % (defaults_base_path, suite_run_data_dir))
    print("")
    print("Project home (%s) and project run data home (%s) successfully created." % (suite_dir, suite_run_data_dir))
    print("")
    print("Add OIMP_PROJECT_HOME=%s and OIMP_PROJECT_RUN_DATA_HOME=%s to your environment variables." % (suite_dir, suite_run_data_dir))