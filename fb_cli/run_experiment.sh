#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

# the experiment name to test
experiment_name=$1
# the context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"
# timestamp for when the experiment started
timestamp=$(date -u +%d-%m-%Y_%H:%M:%S)

function run_experiment_aws_lambda {
  stmsg "Starting experiment for AWS Lambda ..."
  nohup bash "$fbrd/orchestration/run_experiment_aws.sh" "$experiment_name" > $fbrd/logs/$timestamp-$experiment_name-aws_lambda.log 2>&1 &
}

function run_experiment_azure_functions {
  stmsg "Starting experiment for Azure Functions ..."
  # nohup bash "$fbrd/orchestration/run_experiment_azure.sh" "$experiment_name" > $fbrd/logs/$timestamp-$experiment_name-azure_functions.log 2>&1 &
  # TODO setback to nohup
  bash "$fbrd/orchestration/run_experiment_azure.sh" "$experiment_name"
}

function run_experiment_openfaas {
  stmsg "Starting experiment for OpenFaas ..."
  nohup bash "$fbrd/orchestration/run_experiment_openfaas.sh" "$experiment_name" > $fbrd/logs/$timestamp-$experiment_name-openfaas.log 2>&1 &
}

stmsg "Staring to run Experiment: $experiment_name"

# run_experiment_aws_lambda
run_experiment_azure_functions
# run_experiment_openfaas
