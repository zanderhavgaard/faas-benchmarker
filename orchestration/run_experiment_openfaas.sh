#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

# the experiment name to test
experiment_name=$1
# unique experiment idenfifier for the experiments started in parallel for the different cloud providers
experiment_meta_identifier=$2

# ===== create client vm

pmsg "Creating openfaas client vm ..."
bash "$fbrd/orchestration/orchestrator.sh" "$experiment_name" "bootstrap" "openfaas_client_vm"

# ===== create eks cluster and run experiment

pmsg "Creating eks cluster and then running experiment on worker server ..."
bash "$fbrd/orchestration/executor.sh" "$experiment_name" "$experiment_meta_identifier" "openfaas"

# ===== destroy client vm

pmsg "Destorying openfaas client vm ..."
bash "$fbrd/orchestration/orchestrator.sh" "$experiment_name" "destroy" "openfaas_client_vm"

# ===== remove experiment pid file

pmsg "Removing experiment pidfile"

rm -f "/tmp/$experiment_name-openfaas.pid"

smsg "Done running experiment orchestration."
