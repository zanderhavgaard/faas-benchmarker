#!/bin/bash

# import utilities
source "$fbrd/fb_cli/utils.sh"
source "$fbrd/orchestration/lockfile_utils.sh"

valid_commands="bootstrap destroy"
valid_platforms="aws_lambda azure_functions aws_ec2 azure_linuxvm openfaas_client_vm"
# get valid experiment names
experiments=$(ls -I "*.md" "$fbrd/experiments")

# parse inputs
experiment_name=$1
cmd=$2
platform=$3

# validate inputs
# TODO fix check experiment
# if ! listContainsElement "$experiments" "$experiment_name"  ; then errmsg "Invalid experiment" ; exit ; fi
if ! listContainsElement "$valid_commands" "$cmd"           ; then errmsg "Invalid command" ; exit ; fi
if ! listContainsElement "$valid_platforms" "$platform"     ; then errmsg "Invalid platform" ; exit ; fi

# source the correct platform orchestrator
source "$fbrd/orchestration/${platform}_orchestrator.sh"

case "$cmd" in
    bootstrap)
        create_infra_lock "$experiment_name" "$platform"
        bootstrap "$experiment_name"
        ;;
    destroy)
        check_infra_lockfile "$experiment_name" "$platform"
        destroy "$experiment_name"
        release_infra_lock "$experiment_name" "$platform"
        ;;
esac
