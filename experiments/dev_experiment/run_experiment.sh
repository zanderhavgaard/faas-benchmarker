#!/bin/bash

# exit if anything goes wrong
set -e

# name of experiment
# must only contain [a-zA-Z\-] to be parseable by terraform
experiment_name="dev-exp"

# location of experiment files
# should be the name of the directory containing this file
experiment_context="dev_experiment"

# the .py file containing experiment code
experiment_code="dev_experiment.py"

# terraform templates to use
cf_provider="aws_lambda"
# cf_provider="azure_functions"
client_provider="aws_ec2"
# client_provider="azure_linuxvm"

# commands to create/destroy infrastructure
creation_command="create"
destruction_command="destroy"

# generate infrastructure from templates
# bash $fbrd/benchmark/infrastructure_orchestrator.sh \
    # $creation_command \
    # $cf_provider \
    # $client_provider \
    # $experiment_name \
    # $experiment_context

# sleep 30
# python dev_experiment.py $experiment_name

# destroy infrastructure after experiment
bash $fbrd/benchmark/infrastructure_orchestrator.sh \
    $destruction_command \
    $cf_provider \
    $client_provider \
    $experiment_name \
    $experiment_context
