#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

function bootstrap {
    experiment_name=$1
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_cloud_function_env="$experiment_context/$experiment_name-aws_lambda.env"
    remote_env_file="/home/ubuntu/$experiment_name-aws_lambda.env"
    experiment_client_env="$experiment_context/$experiment_name-azure_linuxvm.env"

    cd "$experiment_context/azure_linuxvm"

    pmsg "Initializing terraform ..."
    bash init.sh "$experiment_name"

    pmsg "Creating client vm ..."
    retries=10
    counter=0
    delay=10
    destroy_delay=60
    tf_deployed="false"

    until $tf_deployed ; do

        (( counter++ ))
        if [ $counter = $retries ] ; then
            errmsg "Maximum deployment retries reached, aborting ..."
            exit
        fi

        pmsg "Trying deployment, attempt # $counter / $retries ..."

        terraform apply \
            -auto-approve \
            -compact-warnings \
            -var-file="$experiment_context/$experiment_name.tfvars" \
            -var "env_file=$experiment_cloud_function_env" \
            -var "remote_env_file=$remote_env_file" \
            && tf_deployed="true" \
            && echo \
            && pmsg "Successfully deployed using terraform ..."

        if ! $tf_deployed ; then
            pmsg "Deployment failed, sleeping for $destroy_delay seconds, and then destroying anything that was created ..."
            sleep $destroy_delay
            terraform destroy -auto-approve
            pmsg "Now sleeping for $delay seconds before attempting deployment again ..."
            sleep $delay
        else
            smsg "Successfully deployed infrastructure!"
        fi
    done

    pmsg "Outputting variables to $experiment_name-azure_linuxvm.env ..."
    terraform output > "$experiment_client_env"

    smsg "Done creating client vm."
}

function destroy {
    experiment_name=$1
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_client_env="$experiment_context/$experiment_name-azure_linuxvm.env"

    cd "$experiment_context/azure_linuxvm"

    pmsg "Destroying azure_linuxvm client vm ..."

    terraform destroy \
        -compact-warnings \
        -var-file="$experiment_context/$experiment_name.tfvars" \
        -auto-approve \
        -var "env_file=$experiment_cloud_function_env" \
        -var "remote_env_file=$remote_env_file"

    smsg "Done destroying azure_linuxvm client vm."

    pmsg "Removing experiment environment files ..."

    rm -f "$experiment_client_env"

    pmsg "Done removing environment files."
}
