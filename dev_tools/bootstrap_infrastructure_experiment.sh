#!/bin/bash

set -e
source "$fbrd/fb_cli/utils.sh"
experiment=$1

if [ ! -d "$fbrd/experiments/$experiment" ] ; then errmsg "Invalid experiment name ..." && exit ; fi
pmsg "Bootstrapping all infrastructure for experiment: $experiment ..."

function bootstrap_aws_lambda {
    infra="aws_lambda"
    pmsg "Now bootstrapping $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "bootstrap" "$infra"
}
function bootstrap_azure_functions {
    infra="azure_functions"
    pmsg "Now bootstrapping $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "bootstrap" "$infra"
}
function bootstrap_azure_linuxvm {
    infra="azure_linuxvm"
    pmsg "Now bootstrapping $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "bootstrap" "$infra"
}
function bootstrap_aws_ec2 {
    infra="aws_ec2"
    pmsg "Now bootstrapping $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "bootstrap" "$infra"
}
function bootstrap_openfaas_client_vm {
    infra="openfaas_client_vm"
    pmsg "Now bootstrapping $infra for experiment: $experiment ..."
    bash "$fbrd/orchestration/orchestrator.sh" "$experiment" "bootstrap" "$infra"
}
function bootstrap {
    bootstrap_aws_lambda
    bootstrap_azure_functions
    bootstrap_azure_linuxvm
    bootstrap_aws_ec2
    bootstrap_openfaas_client_vm
}

if [[ "$*" = *--skip-prompt* ]] ; then
    bootstrap
else
    pmsg "This will create ALL infrastructure for experiment: $experiment, would you like to continue? [yes/no]"
    read -n 3 -r ; echo
    if [[ $REPLY =~ ^yes$ ]]; then
        bootstrap
    else
        errmsg "Aborting ..."
    fi
fi
