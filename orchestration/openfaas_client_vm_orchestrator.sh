#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

function bootstrap {
    experiment_name=$1
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_cloud_function_env="$experiment_context/$experiment_name-aws_lambda.env"
    remote_env_file="/home/ubuntu/$experiment_name-aws_lambda.env"
    experiment_client_env="$experiment_context/$experiment_name-openfaas_client_vm.env"

    cd "$experiment_context/openfaas_client_vm"

    pmsg "Initializing terraform ..."
    bash init.sh "$experiment_name"

    pmsg "Creating client vm ..."
    terraform apply \
        -auto-approve \
        -compact-warnings \
        -var-file="$experiment_context/$experiment_name.tfvars"

    pmsg "Outputting variables to $experiment_name-openfaas_client.env ..."
    terraform output > "$experiment_client_env"

    smsg "Done creating client vm."
}

function destroy {
    experiment_name=$1
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_client_env="$experiment_context/$experiment_name-openfaas_client_vm.env"

    cd "$experiment_context/openfaas_client_vm"

    pmsg "Destroying client vm ..."

    terraform destroy \
        -auto-approve \
        -compact-warnings \
        -var-file="$experiment_context/$experiment_name.tfvars"

    smsg "Done destroying client vm."

    pmsg "Removing experiment environment files ..."

    rm -f "$experiment_client_env"

    pmsg "Done removing environment files."
}
