# Overloadimpact

Command line tool and framework for writing and running tests suites for loadimpact.com, with support for custom lua libraries.

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


## Usage

### Set up suite dirs

The first time you run oimp you will need to set a suite dir. If you run oimp now you will get:

```
$ oimp
Traceback (most recent call last):
NameError: OIMP_SUITE dir not found. Set it as OIMP_SUITE_HOME env var, or execute from it's root dir. You can create a suite by running.
```

To fix this create a suite by running:

```
oimp setup_project foo /path/to/parent_of_foo
Add OIMP_SUITE_HOME=/path/to/parent_of_foo/foo_oimp_suite and OIMP_SUITE_RUN_DATA_HOME=/path/to/parent_of_foo/foo_oimp_suite_run_data to your environment variables.
```

Add the environment vars as instructed.

Run `oimp` with no arguments to see all available commands.

```
$ oimp
USAGE:
      oimp setup_project        [NAME] [DEST_DIR]
      oimp sequence         [NAME] [RUN_DESCRIPTION]
      oimp program         [NAME] [RUN_DESCRIPTION]
      oimp test_config        [NAME]
      oimp scenario      [ ACTION] [NAME]
      oimp report program  [ACTION] [PROGRAM_RUN_ID]
      oimp report test_config [ACTION] [RUN_ID] [TITLE]
      oimp target
      oimp api_method        [NAME] [ARGS ...]
      oimp help
```

## Future Ideas

* Enable local running of scenarios. Does not seem too complicated as all request calls are already wrapped in oimp.request(). For local running we could use the luasocket http library (<http://w3.impa.br/~diego/software/luasocket/http.html>) instead, which might be what is actually used by LoadImpact because the function calls are very similar.

## Troubleshooting

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