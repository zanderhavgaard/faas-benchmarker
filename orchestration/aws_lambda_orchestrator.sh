#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

function bootstrap {
    experiment_name=$1
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_cloud_function_env="$experiment_context/$experiment_name-aws_lambda.env"

    cd "$experiment_context/aws_lambda"

    pmsg "Initializing terraform ..."
    bash init.sh "$experiment_name"

    pmsg "Creating cloud functions ..."
    retries=10
    counter=0
    delay=60
    destroy_delay=10
    tf_deployed="false"

    until $tf_deployed ; do

        (( counter++ ))
        if [ $counter = $retries ] ; then
            errmsg "Maximum deployment retries reached, aborting ..."
            exit
        fi

        pmsg "Trying deployment, attempt # $counter / $retries ..."

        terraform apply -auto-approve \
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

    # echo -e "\n--> Outputting variables to experiment.env ...\n"
    pmsg "Outputting variables to $experiment_name-awslambda.env ..."
    terraform output > "$experiment_cloud_function_env"

    smsg "Done creating cloud functions."
}

function destroy {
    experiment_name=$1
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_cloud_function_env="$experiment_context/$experiment_name-aws_lambda.env"

    cd "$experiment_context/aws_lambda"

    pmsg "Destroying cloud functions ..."

    terraform destroy -auto-approve

    smsg "Done destroying cloud functions."

    pmsg "Removing experiment environment files ..."

    rm -f "$experiment_cloud_function_env"

    pmsg "Done removing environment files."
}
