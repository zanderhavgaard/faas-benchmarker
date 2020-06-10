#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

# the experiment name to test
experiment_name=$1
# the context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"
# timestamp for when the experiment started
timestamp=$(date -u +%d-%m-%Y_%H-%M-%S)
# ssh key for the db server
key_file="$fbrd/secrets/ssh_keys/db_server"
# where to store logs on the db server
log_location="/home/ubuntu/logs/orchestration/"
# unique identifier for this round of experiments across providers
experiment_meta_identifier=$(date +%s | sha256sum | base64 | head -c 32 ; echo)

# store process pids to monitor that only one of each orchestrator is running at a time
aws_lambda_pidfile="/tmp/$experiment_name-aws_lambda.pid"
azure_functions_pidfile="/tmp/$experiment_name-azure_functions.pid"
openfaas_pidfile="/tmp/$experiment_name-openfaas.pid"

function check_that_experiment_is_not_running {
  [ -f "$aws_lambda_pidfile" ] && errmsg "Experiment pidfile(s) already exists, you must wait for existing experiment to finish before running again." && exit 1
  [ -f "$azure_functions_pidfile" ] && errmsg "Experiment pidfile(s) already exists, you must wait for existing experiment to finish before running again." && exit 1
  [ -f "$openfaas_pidfile" ] && errmsg "Experiment pidfile(s) already exists, you must wait for existing experiment to finish before running again." && exit 1
}

function run_experiment_aws_lambda {
  stmsg "Starting experiment for AWS Lambda ..."
  aws_lambda_log="$fbrd/logs/$timestamp-$experiment_meta_identifier-$experiment_name-aws_lambda.log"
  pmsg "Logging orchestration to file: $aws_lambda_log"
  nohup bash -c " \
      bash \"$fbrd/orchestration/run_experiment_aws_lambda.sh\" \"$experiment_name\" \"$experiment_meta_identifier\" > $aws_lambda_log 2>&1 \
      ; scp -o StrictHostKeyChecking=no -i $key_file $aws_lambda_log ubuntu@$TF_VAR_db_server_static_ip:$log_location \
      " > /dev/null 2>&1 &
  echo $! > "$aws_lambda_pidfile"
}

function run_experiment_azure_functions {
  stmsg "Starting experiment for Azure Functions ..."
  azure_functions_log="$fbrd/logs/$timestamp-$experiment_meta_identifier-$experiment_name-azure_functions.log"
  pmsg "Logging orchestration to file: $azure_functions_log"
  nohup bash -c " \
      bash \"$fbrd/orchestration/run_experiment_azure_functions.sh\" \"$experiment_name\" \"$experiment_meta_identifier\" > $azure_functions_log 2>&1 \
      ; scp -o StrictHostKeyChecking=no -i $key_file $azure_functions_log ubuntu@$TF_VAR_db_server_static_ip:$log_location \
      " > /dev/null 2>&1 &
  echo $! > "$azure_functions_pidfile"
}

function run_experiment_openfaas {
  stmsg "Starting experiment for OpenFaas ..."
  openfaas_log="$fbrd/logs/$timestamp-$experiment_meta_identifier-$experiment_name-openfaas.log"
  pmsg "Logging orchestration to file: $openfaas_log"
  nohup bash -c " \
      bash \"$fbrd/orchestration/run_experiment_openfaas.sh\" \"$experiment_name\" \"$experiment_meta_identifier\" > $openfaas_log 2>&1 \
      ; scp -o StrictHostKeyChecking=no -i $key_file $openfaas_log ubuntu@$TF_VAR_db_server_static_ip:$log_location \
      " > /dev/null 2>&1 &
  echo $! > "$openfaas_pidfile"
}

stmsg "Starting to run Experiment: $experiment_name"
pmsg "Experiment has meta identifier: $experiment_meta_identifier"

# verify that the experiment is not already running
check_that_experiment_is_not_running

# start the experiment
run_experiment_aws_lambda
run_experiment_azure_functions
run_experiment_openfaas

pmsg "Experiment results will be avilable on the db server once the experiment is complete."
