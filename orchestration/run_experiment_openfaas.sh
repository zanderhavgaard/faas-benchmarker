#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

# the experiment name to test
experiment_name=$1
# unique experiment idenfifier for the experiments started in parallel for the different cloud providers
experiment_meta_identifier=$2

function_provider="openfaas"
client_provider="openfaas_client_vm"

function log_experiment_failed {
    bash "$fbrd/orchestration/experiment_status_updater.sh" \
        "update_failed" \
        "$experiment_name" \
        "$experiment_meta_identifier" \
        "$function_provider" \
        "$client_provider"
    errmsg "Exitting ..."
    exit
}

# ==== log experiment status

bash "$fbrd/orchestration/experiment_status_updater.sh" "insert" "$experiment_name" "$experiment_meta_identifier" "$function_provider" "$client_provider"

# ===== create client vm

pmsg "Creating openfaas client vm ..."
bash "$fbrd/orchestration/orchestrator.sh" "$experiment_name" "bootstrap" "openfaas_client_vm" || log_experiment_failed

# ===== create eks cluster and run experiment

pmsg "Creating eks cluster and then running experiment on worker server ..."
bash "$fbrd/orchestration/executor.sh" "$experiment_name" "$experiment_meta_identifier" "openfaas" || exit

# ===== destroy client vm

pmsg "Destorying openfaas client vm ..."
bash "$fbrd/orchestration/orchestrator.sh" "$experiment_name" "destroy" "openfaas_client_vm" || log_experiment_failed

# ===== remove experiment pid file

pmsg "Removing experiment pidfile"

rm -f "/tmp/$experiment_name-openfaas.pid"

smsg "Done running experiment orchestration."

# ===== log experiment completed

bash "$fbrd/orchestration/experiment_status_updater.sh" "update_completed" "$experiment_name" "$experiment_meta_identifier" "$function_provider" "$client_provider"
