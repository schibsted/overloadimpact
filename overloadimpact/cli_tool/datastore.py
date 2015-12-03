#!/usr/bin/env python
import pprint
import time
import liclient

data_store_version_prefix = ".VER_"


# Upload a new datastore version, and update it for all scenarios
def update_for_scenarios(data_store_name, scenarios, additional_data_stores):
    time_str = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    global data_store_version_prefix
    version_name = data_store_name + data_store_version_prefix + time_str
    print version_name

    file_obj = open('../lua/datastores/' + data_store_name + '.csv', 'r')
    data_store = liclient.client.create_data_store({  # for unknown reasons this returns 500 error
        'name': version_name,
        'from_line': '1',
        'separator': 'comma',
        'delimiter': 'double',
    }, file_obj)
    while not data_store.has_conversion_finished():
        time.sleep(3)
    print("Data store conversion completed with status " + repr(data_store.status))

    print "Created data_store with id " + repr(data_store.id)
    pprint.pprint(data_store)

    # due to a bug in python api we need to recreate whole data store array and set it
    all_data_stores = additional_data_stores
    all_data_stores.append(data_store.id)
    for scenario_id in scenarios:
        user_scenario = liclient.client.get_user_scenario(scenario_id)
        user_scenario.data_stores = []
        user_scenario.data_stores = additional_data_stores
        user_scenario.update()
        print "Updated scenario " + repr(scenario_id)


def get_last_data_store_versions():
    data_stores = liclient.client.list_data_stores()
    versioned_data_stores = {}
    # lookup latest version of that datastore
    for data_store in data_stores:
        prefix_pos = data_store.name.find(data_store_version_prefix)
        if prefix_pos < 1:
            continue
        base_name = data_store.name[:prefix_pos]
        # first version of this data_store found e.g. "foo.VER_201504505123", save with key "foo"/base_name
        if base_name not in versioned_data_stores:
            versioned_data_stores[base_name] = data_store
        else:
            # overwrite if current entry is newer
            if versioned_data_stores[base_name].updated < data_store.updated:
                versioned_data_stores[base_name] = data_store

    # simplify result
    last_data_store_versions = {}
    for base_name in versioned_data_stores:
        last_data_store_versions[base_name] = versioned_data_stores[base_name].name
    return last_data_store_versions
