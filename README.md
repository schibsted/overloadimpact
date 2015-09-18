# overloadimpact

Command line tool for interacting with LoadImpact


# LoadImpact execution scripts

These scripts sets off collections of loadimpact tests, enabling controlled
sequencing and parallel execution of different tests, in order to simulate a
more realistic server load.


## Installation

Before you install the dependencies make sure you have `virtualenv` installed
on your machine (you can install it with `pip install virtualenv`). After that
to install all dependencies you should run:

```
virtualenv .virtual-env                      # Creates a new virtual env
source .virtual-env/bin/activate             # Uses this new virtual env
pip install -r execution/requirements.txt    # Install dependencies in this env
```

After you create the new virtual environment you simply need to activate it
before using the bin tool. Do this by running the 2nd command above.

Before you can run the loadimpact client you also need to set the API token
by setting the following environment variable:

```
export LOADIMPACT_API_TOKEN=YOUR_API_TOKEN_GOES_HERE
```

Add to your shell profile file to avoid doing this all the time.


## Usage

Run `./bin/loadimpact` with no arguments to check all available commands.

```
$ ./bin/loadimpact
    USAGE:
      loadimpact sequence         [NAME] [RUN_DESCRIPTION]
      loadimpact program         [NAME] [RUN_DESCRIPTION]
      loadimpact config        [NAME]
      loadimpact scenario      [NAME]
      loadimpact update        [NAME]
      loadimpact target        [NAME]
      loadimpact report program  [ACTION] [PROGRAM_RUN_ID]
      loadimpact report config [ACTION] [RUN_ID] [TITLE]
      loadimpact method        [NAME] [ARGS ...]
      loadimpact help
```


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