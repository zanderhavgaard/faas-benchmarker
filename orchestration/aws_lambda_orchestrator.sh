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
    tf_deployed="false"
    until $tf_deployed ; do
        terraform apply -auto-approve \
            && tf_deployed="true" \
            && echo \
            && pmsg "Successfully deployed using terraform ..."
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
