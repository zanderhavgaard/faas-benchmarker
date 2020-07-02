```
  __                       _                     _                          _
 / _| __ _  __ _ ___      | |__   ___ _ __   ___| |__  _ __ ___   __ _ _ __| | _____ _ __
| |_ / _` |/ _` / __|_____| '_ \ / _ \ '_ \ / __| '_ \| '_ ` _ \ / _` | '__| |/ / _ \ '__|
|  _| (_| | (_| \__ \_____| |_) |  __/ | | | (__| | | | | | | | | (_| | |  |   <  __/ |
|_|  \__,_|\__,_|___/     |_.__/ \___|_| |_|\___|_| |_|_| |_| |_|\__,_|_|  |_|\_\___|_|
```

A project to benchmark and test the behavior and capabilities of FaaS offerings from public cloud providers and open-source FaaS projects.
The project seeks to increase transparency of closed source FaaS offerings from public cloud providers, by answering questions like: "How long does it take for my function to incur a cold start?", or "When will my function be scaled up due to high demand?".
Further the project strives to make results comparable between cloud platforms, such that users can choose the one that best suits their needs.

![infrastructure overview](diagrams/experiment_infrastructure-all_infra.png)

---

The project is created by [@ThomasKeralla](https://github.com/ThomasKeralla) (thkh@itu.dk) & [@zanderhavgaard](https://github.com/zanderhavgaard) (pezh@itu.dk) as part of our MSc. Thesis @ the IT-University of Copenhagen.

---





# Experiments

faas-benchmarker is built around providing a convenient way of conducting 'experiments'.
An experiment will be run in the same way against the different FaaS platforms, and in repeatable way such that platform changes can be observed over time.


## Experiment Abstraction

faas-benchmarker centers around the 'experiment' abstraction.
The framework allows users to easily create high level experiments that test or benchmark a specific behavior or metric of FaaS platforms.
The faas-benchmarker framework then handles creating sandboxed environments in which the experiment code is executed against different FaaS platforms.
The experiment code consists of a python script based on a template, in which the the logic for the experiment and metrics are specified.
The script utilizes the `Benchmarker` python class which provides a number of commands like 'invoke_function', which will then be translated into actually invoking the specified function on the different platforms.
The framework handles logging generic data from the experiment invocations.
Though experiment specific data are stored in their own tables and have to be added manually.
Using some automated way of logging experiment specific data points would be preferable, but is currently outside the scope of the project.
New experiments are created from a template using the `fb-cli --create-experiment <experiment name>` command.


### Benchmarker Application

Experiments use the Benchmarker python application.
Experiment scripts instantiate a Benchmarker object that handles translating and interfacing with all of the other components.
Chief amoung these are the 'providers' that implement the AbstractProvider class.
The providers thus provide the platform specific implementations of `invoke_function` and `invoke_function_concurrently`, the Benchmarker then dispatches method calls to the correct provider based on how the Benchmarker is configured.
The benchmarker and experiment code is packaged and distributed as a docker image: [faasbencmarker/client](https://hub.docker.com/u/faasbenchmarker) which is used by the client servers when running experiments.
All docker images are currently being built by a circleci pipeline, and distributed through docker hub. The scripts in the `ci` directory make building the pushing the images easy.


TODO insert graph of benchmarker classes


### Experiment Cloud Functions

faasbenchmarker provides 4 generic cloud functions to conduct experiments on.
These are respectively `function1, function2, function3 & monolith`.
Function 1 through 3 is an attempt at creating a generic 'lab' cloud function.
The function* provide a parameterized interface for configuring invocations using JSON.
The parameters are:
- `StatusCode`: int, the statuscode for the invoker, must be 200.
- `sleep`: float, amount of seconds the function should sleep.
- `thoughput_time`: float, amount of seconds to do arbitrary computations.
- `invoke_nested`: list, JSON list with parameters for invoking functions from within the invoked function.

The `monolith` function is an answer to the convention that cloud functions should be as small and atomic as possible, by instead making a big function that contains a lot of different, although arbitrary, functionality, accessed by passing different parameters to the function.
The monolith accepts the following extra parameters as well as the ones described above.
- `args`: int, The complexity of the function to compute.
- `run_function`: string, which function to use.
- `seed`: int, seed to use for randomness.


Following is a example of invoking function1, which will perform a nested invocation of function2, which in turn will perform a nested invocation of function3.

```python
invoke_nested = [
    {
        "function_name": f"{experiment_name}-function2",
        "invoke_payload": {
            "StatusCode": 200,
            "invoke_nested": [
                    {
                    "function_name": f"{experiment_name}-function3",
                    "invoke_payload": {
                        "StatusCode": 200,
                        }
                    },
                    {
                    "function_name": f"{experiment_name}-function3",
                    "invoke_payload": {
                        "StatusCode": 200,
                        }
                    }
                ]
            }
        }
    ]
benchmarker.invoke_function(function_name='function1',
                            function_args={"invoke_nested":invoke_nested})
```

Example of using `invoke_function_concurrently` to invoke function1 7 times in parallel.

```python
args = {
    'throughput_time': 0.2
}
response = benchmarker.invoke_function_conccurrently(
  function_name='function1',numb_threads=7,function_args=args)
```

## Creating Experiments

Creating a new experiment is done by using the `fb-cli` tool.
Invoking the `--create-experiment` and providing an experiment name will copy all of the relevant templates and modify them for the experiment.
The new experiment will consist of a `<experiment name>.py` which is the expreiment logic and a `<experiment name>.tfvars` which are experiment specific tweaks to the terraform templates.
As well as a number of directories containing the experiment specific infrastructure.
In order ensure that experiments are as reproducible as possible, each experiment has it's own infrastructure.
Thus when an experiment is run, fresh cloud function instances and client servers are created to conduct the experiment.
All of the infrastructure files are automatically generated and should not be edited manually.
If changes are made to the templates, the templates for each experiment will need to be regenerated using the `fb-cli --update-experiment-infrastructure-templates` command.
Thus when writing a new experiment only the `<experiment name>.py` file should be edited, and perhaps the `<experiment name>.tfvars`, if the experiment needs a larger client server for more concurrency etc.


# Architecture
The architecture of faas-benchmarker is divided into three main parts, the `permanent infrastructure`, the `cloud functions` and the `experiment infrastructure`.

Currently the permanent infrastructure is hosted on Digital Ocean. Experiments are conducted on mix of AWS and Azure resources. The use of different cloud providers is make the most of the different free/student offerings, as well as to utilize different cloud-specific tools.


## Permanent Infrastructure
The permanent infrastructure consists of two servers, the `orchestrator` and the `database` servers, as well as a blob storage.
The purpose of the orchestrator is to orchestrate the experiments; managing experiment lifecycles, bootstrapping and destroying experiment infrastucture, running experiment code.
The database server hosts a sql database with experiment results and log files from experiment runs.
The permanent infrastructure is currently hosted on two Digital Ocean droplets (linux vms), though if desired these could easily be moved to another cloud provider, or even self hosted.


## Cloud Functions
Currently faas-benchmarker supports `AWS lambda`, `Azure Functions` and `OpenFaaS`. 'Support' for a cloud function platform consists of an implemtation of the 'lab functions' as described above, as well as a 'provider' python class to interface the framework with the cloud function platform.
The different cloud funtions are created as needed from templates using terraform.
AWS Lambda and Azure Functions run on their respective clouds, OpenFaaS is bootstrapped into a AWS EKS Fargate cluster.
EKS on Fargate is AWS managed kubernetes but running purely in Fargate containers, which means that the cluster is 'serverless'.
Which means that OpenFaaS function containers can be scaled independently of the rest of the cluster, thus providing the most 'serverless' way of running OpenFaaS
We use this specific deployment in order to have the most comparable deployment of OpenFaaS with AWS Lambda and Azure Functions.

### Support for New Cloud Function Platforms
Adding support for new cloud function platforms consists of lab function implementation, the python provider, terraform templates, as well as an orchestration script that handles all of the different quirks of the platform in question, that can be run in the framework.


## Experiment Infrastructure




# Orchestration

## Terraform

## fb-cli





# Results Report

## Generating a Report

TODO


# Developement

## Running Experiments Locally
