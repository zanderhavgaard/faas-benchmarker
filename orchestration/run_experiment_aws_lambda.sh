#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

# provision infrastructure, run experiment code and then destroy infrastructure

# the experiment name to test
experiment_name=$1
# unique experiment idenfifier for the experiments started in parallel for the different cloud providers
experiment_meta_identifier=$2

function_provider="aws_lambda"
client_provider="azure_linuxvm"

function log_experiment_failed {
    bash "$fbrd/orchestration/experiment_status_updater.sh" \
        "update_failed" \
        "$experiment_name" \
        "$experiment_meta_identifier" \
        "$function_provider" \
        "$client_provider"
}

# ==== log experiment status

bash "$fbrd/orchestration/experiment_status_updater.sh" "insert" "$experiment_name" "$experiment_meta_identifier" "$function_provider" "$client_provider"

# ===== create infrastructure

pmsg "Bootstrapping cloud functions ..."
bash "$fbrd/orchestration/orchestrator.sh" "$experiment_name" "bootstrap" "aws_lambda" || log_experiment_failed

pmsg "Bootstrapping client vm ..."
bash "$fbrd/orchestration/orchestrator.sh" "$experiment_name" "bootstrap" "azure_linuxvm" || log_experiment_failed

# ====== run experiment

pmsg "Running experiment ..."
bash "$fbrd/orchestration/executor.sh" "$experiment_name" "$experiment_meta_identifier" "aws_lambda" || log_experiment_failed

# ====== destroy infrastructure

pmsg "Destroying cloud functions ..."
bash "$fbrd/orchestration/orchestrator.sh" "$experiment_name" "destroy" "aws_lambda" || log_experiment_failed

pmsg "Destroying client vm ..."
bash "$fbrd/orchestration/orchestrator.sh" "$experiment_name" "destroy" "azure_linuxvm" || log_experiment_failed

# ===== remove experiment pid file

pmsg "Removing experiment pidfile"

rm -f "/tmp/$experiment_name-aws_lambda.pid"

smsg "Done running experiment orchestration."

# ===== log experiment completed

bash "$fbrd/orchestration/experiment_status_updater.sh" "update_completed" "$experiment_name" "$experiment_meta_identifier" "$function_provider" "$client_provider"
