

## Environment setup

### AWS CLI
```
git clone https://github.com/remap/cibic21-exhibit.git && cd cibic21-exhibit
virtualenv -p python3 env && source env/bin/activate
pip install awscli boto3
complete -C aws_completer aws
aws configure
```

### TouchDesigner

* sample_project.toe is setup to read Python import paths from sys-paths.txt file, to generate this file, run:
```
./get-module-path.sh
```
* before opening the project, create `img_cache` folder next to it (it is needed for `file_fetcher.tox`).

> ⚠️ On macOS TouchDesginer uses Python 3.7 which has old version of urllib3 [incompatible with boto3](https://github.com/boto/botocore/issues/2580). Just replace it with newer version from your virtualenv at `TouchDesigner.app/Contents/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages/urllib3`

If you're running TouchDesigner on Windows, something might not work. Take a look at how the project is set up by inspecting these paths:
* `/_sys_paths`
* `/project1/local/modules`
  * `td_utils`
  * `aws`

`modules` has custom parameters to setup AWS helper code. It will expect AWS credentials named "sudomagic-dev" or "sudomagic-exhibit" in your ".aws/credentials" file. 



## CiBiC 2021 TouchDesigner Components
### module.tox

This component contains helper functions that can be called using [MOD class in TouchDesigner](http://derivative.ca/wiki088/index.php?title=MOD_Class). For example, one could call from anywhere in TouchDesigner `mod.aws.snsClient.list_topics()`.

> !!! This module is expected to be updated with more functions as we progress. Please make sure you have the latest version.

#### Setup

In order for this to work, this module must be place inside "local" component (create it if it doesn't exist) under your project (e.g. "/project1", not root!).

#### Functions list

Every function is documented: to access function full documentation use [docstrings](https://www.python.org/dev/peps/pep-0257/#what-is-a-docstring), for example in Textport, type (assuming your modules is in "/project1/local") `print(mod('/project1/local/modules/td_utils').setOpError.__doc__)`.

* `mod.td_utils.setOpError()` -- sets operator error message;
* `mod.td_utils.clearOpError()` -- clears operator error message;
* `mod.td_utils.runAsync()` -- runs function asynchronously in a separate thread and delivers result through the supplied callback.


### file_fetcher.tox

This module allows to asynchronously download media given list of URLs.

#### Inputs

* Input1: `TableDAT`
	* 1 column: list of URLs

#### Outputs

* Output1: `TableDAT`
	* 2 columns: `original_url` and `full_file_path`

* Output2: `CHOP`
	* `inProgress` -- boolean value that shows whether the module is processing or not;
	* `nFetched` -- number of files fetched.

#### Parameters

* `Cache Folder` -- specify cache folder where downloaded media will be stored (default is `<project_dir>/fetcher_cache`)
* `Cache Size` -- maximum number of files maintained in the cache; if number of downloaded files is bigger than this number, cache will be increased temorarily to accommodate all fresh downloads.

> ☝️ Check out the [video](https://youtu.be/-bDQ_DcRONY) that shows `er_rekognition.tox` and `file-fetched.tox` modules in action.

### sns_pub.tox

This component allows to publish arbitrary messages to a SNS topic (asynchronously, [modules.tox](#modules.tox) must be setup!) specified by topic name.

#### Parameters

* `SNS Topic` -- SNS topic name;
* `Publish` -- will trigger SNS publishing.

#### Inputs

* `DAT In` -- TextDAT, which contents will become SNS message's body.

#### Outputs

* `CHOP Out` -- "status" variable (0 - ok, 1 - error, 2 - processing);
* `DAT Out` -- table with execution result/process.

### sns_receiver.tox

This component allows to receive messages from an arbitrary SNS topic (asynchronously, [modules.tox](#modules.tox) must be setup!) specified by topic name.

#### Parameters

* `Init` -- will initialize for receiving SNS messages;
* `SNS Topic` -- SNS topic name.

#### Inputs

None.

#### Outputs

* `Dat Out` -- latest message received: 2 columns `timestamp` and `payload_json`.

> Note: since SNS messages may arrive out of order, component checks timestamps of the received messages and outputs if received messages *only* comes after the previously received (i.e. only the latest message is output at any given time). To see last 10 messages, check `response_fifo` DAT inside the component.
