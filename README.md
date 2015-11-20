# Overloadimpact

Command line tool and framework for writing and running tests suites for loadimpact.com, with support for custom lua libraries.

The tool uses the LoadImpact [Python SDK](http://developers.loadimpact.com/sdk/index.html#li-docs-sdk-python) and [API](http://developers.loadimpact.com/api/).

Overloadimpact can fire sets of test_configs, create reports and statistics, and reuse code between test scenarios.


## Installation

### overloadimpact pip module

If you clone from git, you can install the pip module locally by running:

```
pip install -e /path/to/overloadimpact
```

### API token environment variable

Before you can run the loadimpact client you also need to set the API token
by setting the following environment variable:

```
export LOADIMPACT_API_TOKEN=YOUR_API_TOKEN_GOES_HERE
```

Add to your shell profile file to avoid doing this all the time.

## Concepts and terminology

#### oimp
The overloadimpact command line tool for is called ```oimp```. The main lua lib for writing scenarios is also called ```oimp```.

#### scenario
The user scenario concept is defined by LoadImpact. It is a a file of lua code performing some user interaction.

#### test_config
The test_config concept is defined by LoadImpact and is a set of one or more scenarios to be executed together.

#### program
A program is a set of test_configs to be executed together. LoadImpact normally limits us to three simultaneous test_configs running. On running a program the test_configs will be reconfigured according scenarios listed under each config setting in the program.

#### sequence
A sequence is a sequence of programs to be executed one after another.

#### report
Reports are html reports with svg charts displaying the results of runs.

#### target
Targets are a set of load targets (requests/s goals) defined in

#### action
An action can either be a flow of actions (e.g. a full login procedure) or a single request (i.e. an API request). This concept is used to be able to measure how many actions the system can handle.

#### project_dir
The project_dir holds your scenarios, custom lua libs, and suite configuration yml files. The yml files define scenarios, test_configs, programs, sequences and targets.

To be able to write and run load impact tests you must first set up a project with the ```oimp setup_project``` command as explained below. Keep this dir in a git repo to share scenarios other test files in the team.

#### project_run_data_dir

This dir holds the record of executed test_config and the reports generated after the test_config runs. The project_run_data_dir is set up with ```oimp setup_project``` as explained below.

In the project_run_data_dir we will find a ```reports``` and a ```runs``` directory. Only the ```runs``` directory needs to be added to git, because the reports take up a lot of space and can be recreated based on the data un ```runs```. We suggest maintaining project_run_data_dir in git to keep a record of executed runs. It is possible to keep the reports dir in Dropbox or somewhere similar to avoid having the whole team creating reports whenever they are needed.

## Usage

### Set up project dirs

The first time you run oimp you will need to set a project dir. If you run oimp now you will get:

```
$ oimp
Traceback (most recent call last):
NameError: OIMP_PROJECT dir not found. Set it as OIMP_PROJECT_HOME env var, or execute from it's root dir. You can set up a new project with: oimp setup_project [name] [destination path].
```

To create a project, run oimp setup_project:

```
$ oimp setup_project bar /tmp/foo
OIMP_PROJECT dir not found. Set it as OIMP_PROJECT_HOME env var, or execute from it's root dir.
You can set up a new project with: oimp setup_project [name] [destination path].

Project home (/tmp/foo/bar_oimp_project) and project run data home (/tmp/foo/bar_oimp_project_run_data) successfully created.

Add OIMP_PROJECT_HOME=/tmp/foo/bar_oimp_project and OIMP_PROJECT_RUN_DATA_HOME=/tmp/foo/bar_oimp_project_run_data to your environment variables.
```

We add the environment vars as instructed.

```
$ export OIMP_PROJECT_HOME=/tmp/foo/bar_oimp_project
$ export OIMP_PROJECT_RUN_DATA_HOME=/tmp/foo/bar_oimp_project_run_data
```

To test that it is working, you can list the example programs created as part of the example project:

```
$ oimp program
                                        PROGRAM
-----------------  -------------------  ----------------------------------------------------
example-program-1
                   example-config-1     1000/10/5
                   _        scenarios:  (example-scenario-2 (70%), example-scenario-3 (30%))

example-program-2
                   example-config-1     1500/10/5
                   _        scenarios:  (example-scenario-2 (70%), example-scenario-3 (30%))

```

Run `oimp help` to see all available commands.

<!--- start help -->
```
$ oimp help

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
            List all defined test_configs defined in
            your_oimp_project_dir/suite_config/scenarios.yaml
      oimp test_config [NAME]
            Execute test config [NAME]

  program:
      A program is a set of test_configs to be executed together. LoadImpact normally
      limits us to three simultaneous test_configs running. On running a program the
      test_configs will be reconfigured according scenarios listed under each config setting
      in the program.

      oimp program
            List the names of all defined programs defined in
            your_oimp_project_dir/suite_config/programs
      oimp program [NAME] [RUN_DESCRIPTION]
            Execute the program [NAME]
            NAME - The name of the program definition file to be executed.
            RUN_DESCRIPTION - Something like "20 web fronts, Redis DB". Mandatory
            description of setup.

  sequence:
      A sequence is a sequence of programs to be executed one after another.

      oimp sequence
            List the names of all defined sequences defined in
            your_oimp_project_dir/suite_config/sequences
      oimp sequence [NAME] [RUN_DESCRIPTION]
            Execute the sequence [NAME]
            NAME - The name of the sequence definition file to be executed.
            RUN_DESCRIPTION - Something like "20 web fronts, Redis DB". Mandatory
            description of setup.

  report:
      Reports are html reports with svg charts displaying the results of runs.

      oimp report program
            List the PROGRAM_RUN_ID for all program executions.
      oimp report program completed [PROGRAM_RUN_ID]
            Create a report for a completed program run.
      oimp report program running [PROGRAM_RUN_ID]
            Create a dynamically updating report for a program run currently being
            executed.
      oimp report program combine [PROGRAM_RUN_ID,PROGRAM_RUN_ID,...]
            Create a combined comparative report for a set of completed program runs.
      oimp report test_config
            List the RUN_ID for all test_config executions.
      oimp report test_config completed [RUN_ID] [TITLE]
            Create a report for a completed test_config run.
            TITLE - optional title for report.
      oimp report test_config running [RUN_ID] [TITLE]
            Create a dynamically updating report for a test_config run currently being
            executed.
            TITLE - optional title for report.

  targets:
      Targets are a set of load targets (requests/s goals) defined in
      your_oimp_project_dir/suite_config/targets.yml.
      They are used in reports to compare actual numbers with what we aim at reaching.

      oimp target
            List targets

  api_method:
      api_method allows custom calls to the LoadImpact API endpoints.

      oimp api_method [NAME] [ARGS ...]
```
<!--- end help -->

## Writing scenarios

### Example scenario

When a project is set up with oimp setup_project, an example scenario called example-scenario-1.lua has been created.

Here is the content of example-scenario-1.lua:
```
local foo_res = foo.foo_request("bar")
if oimp.fail(page, 'foo_request', foo_res, nil) then
  oimp.done(0)
  return
end
```

It calls the function foo_request from the example ```foo``` lib found in lib/foo/foo.lua:

```
foo = {}
foo.some_var = "bar"

function foo.some_request(foo_param)
  local page = "foo_index"
  local users_ds  = datastore.open('users-DS_VERSION') -- get a versioned users DS
  local user = users_ds:get_random()
  local url = "http://www.examplefoo.com/index.html?user_email=" .. url.escape(user[1]) .. "&foo=" .. url.escape(foo_param)
  return oimp.request(page,
                      {
                        'GET',
                        url,
                      },
                      true -- is_core_action = true, signals that this the core action of this scenario
  )
end
```

### Libs

OverloadImpact provide some general utility libs.

* [oimp](overloadimpact/lua/lib/common/oimp.lua) provides a few general functions for writing tests with metrics.
* [logger](overloadimpact/lua/lib/common/logger.lua) provides logger functions.
* [cookies](overloadimpact/lua/lib/common/cookies.lua) provides cookie manipulation functions.
* [redirect](overloadimpact/lua/lib/common/redirect.lua) provides redirect looping functions, especially useful when doing custom cookie handling.

#### Lib loading

The default libs are always loaded. You can also add your own custom libs. An example is the foo lib created in ```your_oimp_project_dir/lua/lib/foo/foo.lua```. It is loaded since it is included in ```your_oimp_project_dir/lua/lib/includes.lua```:

```
-- Add your includes here. "foo" is a subdir in in this dir.
--- import foo/foo.lua"
```

#### Scenario composition

All scenarios are, when uploaded to loadimpact with the oimp command line tool, composed of the libraries to include, a scenario header, the scenario itself and a scenario footer. The header and footer handles metric setup and metrics success reporting. The composition is done in [code.py](overloadimpact/cli_tool/code.py).

#### Lua configuration

The default config settings can be found in [oimp_config](overloadimpact/lua/lib/common/oimp_config.lua). To override these settings, edit the ```your_oimp_project_dir/lua/config/suite_config.lua```.

The oimp_config.TARGET_SERVER must be set in order to handle redirect loops correctly:

```
oimp_config.TARGET_SERVER = "http://www.example.com"
```

### Metrics

OverloadImpact bases the statistics and charts gathered on data obtained through the LoadImpact API. Some of the data is default metrics, some of it is custom metrics created by oimp lib functions.

#### Page argument

To a number of the oimp functions we pass a page argument. This argument is a tag for timing and correctness metrics. E.g. if you are doing a POST request of a pupil in a school API, you could call set page to 'pupil_create'.

#### Correctness

The correctness metric is the average success rate across all scenario runs. To signal that a scenario fails you must do two things:

Call ```oimp.done(0)``` and return from the top scope. In example-scenario1.lua we see:

```
local foo_res = foo.foo_request("bar")
if oimp.fail(page, 'foo_request', foo_res, nil) then
  oimp.done(0)
  return
end
```

A scenario which does not return will mark the test as successful in its generated footer functions. A scenario which does not call ```oimp.done()``` is not reporting its correctness rate.

We will now explain some useful oimp functions found in the [oimp utilities lib](overloadimpact/lua/lib/common/oimp.lua).


##### Result check functions
These are functions for evaluating values.

###### oimp.fail(page, metric_tag, value, failure)
Perform a negative test. It returns false if the value matches the failure one. Example:
```
local foo_res = foo.foo_request("bar")
if oimp.fail(page, 'foo_request', foo_res, nil) then
  oimp.done(0)
  return
end
```

###### oimp.check_status(page, res, expected)
Test if request result status_code matched the expected status_code
```
local foo_res = foo.foo_request("bar")
if not oimp.check_status(page, foo_res, 200) then
  oimp.done(0)
  return
end
```

###### oimp.pass(page, metric_tag, value, correct)
Perform a positive test. It returns true if the value matches the correct one, adding a pass value
for this specific metric_tag. It calls oimp.error() on failure.
```
local foo_res = foo.foo_request("bar")
if oimp.pass(page, "foo_index", foo_res['status_code'], 200) then
   -- do something
else
  oimp.done(0)
  return
end
```


#### Core action count

Some scenarios will iterate over some action multiple times. An example could be an API endpoint test which first obtains a an API token, an then uses this token 100 times to hit the endpoint. In this case we must mark this request to be counted, in order to get a total count of actions performed.

#### xhprof profiling

You can trigger xhprof profiling of a request by using oimp.profile(). For every X (defined by the int var oimp_config.PROFILE_EACH) executions approximately one will get supplied an ```_x=page_name``` argument, in order to trigger xhprof. It is not supplied to every request to prevent profiling slowing down the service.

An example:

```
url = oimp.profile(url, page)
```

## Uploading and running scenarios on LoadImpact

### Uploading a scenario

To be able to upload a scenario to loadimpact.com you must first create a scenario manually on that web site and get its ID (the number in the url). Add the scenario id to ```your_oimp_project_dir/suite_config/scenarios.yml```:

```
scenarios:
  foo-scenario:
    id: 3071351
```

The name does not have to match the name of the scenario on loadimpact.com, but for clarity it is good to use the same name.

### Adding a test_config

You must create a test_config on loadimpact.com to be able to execute one or more scenarios massively. The name of the test_config does not have to match the name in your suite_config, but out of convenience name it without spaces. Let's call it "mixed-api-traffic". Then add it, together with the id from the URL, to ```your_oimp_project_dir/suite_config/configs.yml```:

```
configs:
  mixed-api-traffic:
    id: 3012689
```

#### Configuring the test_config

The test_config can either be configured using the loadimpact.com web interface or by an oimp program. We will explain programs below. Note that programs will overwrite settings done on the web.

### Creating a program

A program is a set of test_configs to be executed together. LoadImpact normally limits us to three simultaneous test_configs running. On running a program the test_configs will be reconfigured according scenarios listed under each config setting in the program.

Unlike test_configs and scenarios, the program does exist as a loadimpact concept, only as an overloadimpact concept. So there is no need to create a program on loadimpact.com to match the program defined locally in ```your_oimp_project_dir/suite_config/programs```.

In the example project we will look at the program ```suite_config/programs/example-program-1.yaml```:

```
---
configs:
  example-config-1:
    users: 1000
    warmup: 10
    stable: 5
    scenarios:
      example-scenario-1:
        percent-of-users: 100
  example-config-2:
    users: 1000
    warmup: 10
    stable: 5
    scenarios:
      example-scenario-2:
        percent-of-users: 70
      example-scenario-3:
        percent-of-users: 30
```

The filename, excluding the extension, is the name of the program e.g. "example-program-1". This name will be used to execute it and generate execution names.

#### Programs reconfiguring test_configs

The program will reconfigure the configs example-config-1 and example-config-2, overwriting existing settings. The config names must correspond to entries in ```your_oimp_project_dir/suite_config/configs.yml```.

Program fields explained:

* test_config parameters
  * ```users``` - the amount of VUs (virtual users) to be used for this test_config. Your total VU limit (e.g. 5000) has to be divided between your test_configs.
  * ```warmup``` - Time in minutes for the build up from 0 to ```users``` amount of users. The amount needed depends both on how much VUs you need to get into action and how long time your platform needs for scaling up. For a 1000 users 10m warmp may be sufficient. Note that if you have multiple test_configs to be executed simultaneously you should give them the same warmup and stable parameters to be run at the same time.
  * ```stable``` - Time in minutes for the stable period. One strategy is to have stable be half of the warmup time.
* scenario parameters
  * ```percent-of-users``` - The amount of the ```users``` to be used on this specific scenario. You must ensure they manually sum up to 100. Otherwise the API will throw an error.
  * ```source-ip-multiplier``` - To improve throughput it may help to spread out tests across IPs. To achieve it we use the ```source-ip-multiplier``` param which can be set from 1-6 representing 1x - 6x multipliers. If it is not set, 1x is assumed. Internally in oimp, there are some peculiar details here. Skip this if you are not interested :). The current implementation of the loadimpact.com API does not have clear implementation of what multiplier param values are excepted to represent each multiplier. LoadImpact's own explanation does not correspond with how it is calculated in practice: *"Start with the number of VU you want to run in your test, say 1501 and multiply with your factor, say 5 X. That's a sum of 7505. Divide by 500 and you have 15.01. You can' have .01 load generators so it will become 16. Always adjusted upwards when not divisible as a whole by 500."* So to work around it, we start with the suggested 0-5 values multiplied by 500s, and then increment by one until the value is accepted by the SDK ```test_config.update()```.
  * ```region``` - We have only managed to use amazon regions, even if some rackspace regions are listed by the API. The default region for oimp is "amazon:ie:dublin". Some example regions are "amazon:us:ashburn", "amazon:us:portland", "amazon:ie:dublin" and "amazon:us:palo alto". In order to work around loadimpact.com system failures and undocumented suspected request limiting we had to run some test from other regions than "amazon:ie:dublin". Also, by spreading scenarios across regions we can force more IPs, and in that way improve request volume.
  * ```multi-regions``` - Automatically spread the traffic for a scenario across Dublin, Ashburn, Portland and Palo Alto.
  * ```use-alternative-regions``` - If ```true```, use Singapore, Sydney, Tokyo instead of the the Western ones. This is a hack to work around system failures in loadimpact.com.

You can see the region and ip multiplier params used in the [example-program-3](overloadimpact/default_project_dirs/oimp_project/suite_config/programs/example-program-3.yaml).


## TODO / Future Ideas

* Improve our inexpert lua and python code.
* All python command failures and exits should have a sensible error message.
* Enable local running of scenarios. Does not seem too complicated as all request calls are already wrapped in oimp.request(). For local running we could use the luasocket http library (<http://w3.impa.br/~diego/software/luasocket/http.html>) instead, which might be what is actually used by LoadImpact because the function calls are very similar.
* Add tests for the code in this repo?

## Troubleshooting

There used to be a couple of bugs in the loadimpact sdk which are currently (20151120) fixed in the [develop branch](https://github.com/loadimpact/loadimpact-sdk-python/).

Here are the bugs:

I debugged a 415 problem I got on update requests from the loadimpact python
API. It's caused by a missing `Content-Type` header. Fixed it by adjusting the
file `/Library/Python/2.7/site-packages/loadimpact/clients.py`:

```python
def put(self, path, headers=None, params=None, data=None,
file_object=None):
```

to:

```python
def put(self, path, headers={"Content-Type": "application/json"},
params=None, data=None, file_object=None):
```

Another bug in obtaining custom metrics was fixed by this [commit](https://github.com/loadimpact/loadimpact-sdk-python/commit/dcd60cf5f23d64876b181bb023dbe073a56210ed]).