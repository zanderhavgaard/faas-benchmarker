#!/bin/bash

set -e
source "$fbrd/fb_cli/utils.sh"
experiment=$1

if [ ! -d "$fbrd/experiments/$experiment" ] ; then errmsg "Invalid experiment name ..." && exit ; fi
pmsg "Destroying all infrastructure for experiment: $experiment ..."

function destroy_aws_lambda {
    infra="aws_lambda"
    pmsg "Now destroying $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "destroy" "$infra"
}
function destroy_azure_functions {
    infra="azure_functions"
    pmsg "Now destroying $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "destroy" "$infra"
}
function destroy_azure_linuxvm {
    infra="azure_linuxvm"
    pmsg "Now destroying $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "destroy" "$infra"
}
function destroy_aws_ec2 {
    infra="aws_ec2"
    pmsg "Now destroying $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "destroy" "$infra"
}
function destroy_openfaas_client_vm {
    infra="openfaas_client_vm"
    pmsg "Now destroying $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "destroy" "$infra"
}

if [[ "$*" = *--skip-prompt* ]] ; then
    destroy_aws_lambda
    destroy_azure_functions
    destroy_azure_linuxvm
    destroy_aws_ec2
    destroy_openfaas_client_vm
else
    pmsg "This will destroy ALL infrastructure for experiment: $experiment, would you like to continue? [yes/no]"
    read -n 3 -r ; echo
    if [[ $REPLY =~ ^yes$ ]]; then
        destroy_aws_lambda
        destroy_azure_functions
        destroy_azure_linuxvm
        destroy_aws_ec2
        destroy_openfaas_client_vm
    else
        errmsg "Aborting ..."
    fi
fi
