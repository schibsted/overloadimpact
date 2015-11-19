import os

def setup(name, dest_dir):
    if not os.path.isdir(dest_dir):
        print("Please supply a valid destination dir")
        return

    defaults_base_path = os.path.dirname(os.path.realpath(__file__)) + "/../default_project_dirs"
    project_dir = os.path.abspath("%s/%s_oimp_project" % (dest_dir, name))
    project_run_data_dir = os.path.abspath("%s/%s_oimp_project_run_data" % (dest_dir, name))
    os.system("cp -rf %s/oimp_project %s" % (defaults_base_path, project_dir))
    os.system("cp -rf %s/oimp_project_run_data %s" % (defaults_base_path, project_run_data_dir))
    print("")
    print("Project home (%s) and project run data home (%s) successfully created." % (project_dir, project_run_data_dir))
    print("")
    print("Add OIMP_PROJECT_HOME=%s and OIMP_PROJECT_RUN_DATA_HOME=%s to your environment variables." % (project_dir, project_run_data_dir))