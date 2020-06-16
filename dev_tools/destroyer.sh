#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

experiment=$1

pmsg "Destroying infrastructure for experiment: $experiment ..."

function destroy_infra {
    infra=$1
    pmsg "Making sure that terraform is initialized ..."
    cd "$fbrd/experiments/$experiment/$infra"
    bash init.sh "$experiment"

    pmsg "Now destroying $infra for experiment: $experiment ..."
    yes | terraform destroy -auto-approve

    pmsg "Removing any lockfiles ..."
    rm -f ./*.lock
}

function remove_env_files {
    pmsg "Removing any experiment env files ..."
    cd "$fbrd/experiments/$experiment"
    rm -f ./*.lock
}

function destroy {
    destroy_infra "aws_lambda" &
    destroy_infra "azure_functions" &
    destroy_infra "azure_linuxvm" &
    destroy_infra "aws_ec2" &
    destroy_infra "openfaas_client_vm" &
    remove_env_files &
}

destroy

smsg "Done destroying infrastucture for experiment: $experiment"
