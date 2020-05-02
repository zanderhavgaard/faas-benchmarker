#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

# the experiment name to test
experiment_name=$1
# the context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"


function run_experiment_aws {
  stmsg "Starting experiment for AWS Lambda"
  # TODO add nohup?
  bash "$fbrd/orchestration/run_experiment_aws.sh" "$experiment_name"
}

stmsg "Staring to run Experiment: $experiment_name"
run_experiment_aws
