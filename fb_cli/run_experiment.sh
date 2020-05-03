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

function run_experiment_aws_lambda {
  stmsg "Starting experiment for AWS Lambda ..."
  aws_lambda_log="$fbrd/logs/$timestamp-$experiment_name-aws_lambda.log"
  pmsg "Logging orchestration to file: $aws_lambda_log"
  nohup bash -c " \
      bash \"$fbrd/orchestration/run_experiment_aws.sh\" \"$experiment_name\" > $aws_lambda_log 2>&1 \
      ; scp -i $key_file $aws_lambda_log ubuntu@$TF_VAR_db_server_static_ip:$log_location \
      " > /dev/null 2>&1 &
}

function run_experiment_azure_functions {
  stmsg "Starting experiment for Azure Functions ..."
  azure_functions_log="$fbrd/logs/$timestamp-$experiment_name-azure_functions.log"
  pmsg "Logging orchestration to file: $azure_functions_log"
  nohup bash -c " \
      bash \"$fbrd/orchestration/run_experiment_azure.sh\" \"$experiment_name\" > $azure_functions_log 2>&1 \
      ; scp -i $key_file $azure_functions_log ubuntu@$TF_VAR_db_server_static_ip:$log_location \
      " > /dev/null 2>&1 &
}

function run_experiment_openfaas {
  stmsg "Starting experiment for OpenFaas ..."
  openfaas_log="$fbrd/logs/$timestamp-$experiment_name-openfaas.log"
  pmsg "Logging orchestrion to file: $openfaas_log"
  nohup bash -c " \
      bash \"$fbrd/orchestration/run_experiment_openfaas.sh\" \"$experiment_name\" > $openfaas_log 2>&1 \
      ; scp -i $key_file $openfaas_log ubuntu@$TF_VAR_db_server_static_ip:$log_location \
      " > /dev/null 2>&1 &
}

stmsg "Starting to run Experiment: $experiment_name"

# run_experiment_aws_lambda
# run_experiment_azure_functions
run_experiment_openfaas

pmsg "Now waiting for experiments to finish ..."
