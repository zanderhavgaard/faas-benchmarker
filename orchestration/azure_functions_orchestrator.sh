#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

function bootstrap {
    experiment_name=$1
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_cloud_function_env="$experiment_context/$experiment_name-azure_functions.env"

    cd "$experiment_context/azure_functions"

    pmsg "Initializing terraform ..."
    bash init.sh "$experiment_name"

    pmsg "Creating cloud functions ..."
    terraform apply -auto-approve

    pmsg "Fixing broken terraform azure function code deployment ..."

    # reupload function code but with dependencies....
    function_code_dirs=$(ls function_code/)
    for fcd in $function_code_dirs; do
        pmsg "Fixing deployment of azure function: $fcd"
        cd "$experiment_context/azure_functions/function_code/$fcd"
        func azure functionapp publish $fcd
    done

    cd "$experiment_context/azure_functions"

    pmsg "Outputting variables to $experiment_name-azure_functions.env ..."
    terraform output > "$experiment_cloud_function_env"

    smsg "Done creating cloud functions."
}

function destroy {
    experiment_name=$1
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_cloud_function_env="$experiment_context/$experiment_name-azure_functions.env"

    cd "$experiment_context/azure_functions"

    pmsg "Destroying cloud functions ..."

    terraform destroy -auto-approve
    # azure sometimes needs a little persuasions to actually destroy everything...
    # so we do it again just to be sure ...
    terraform destroy -auto-approve

    smsg "Done destroying cloud functions."

    pmsg "Removing experiment environment files ..."

    rm "$experiment_cloud_function_env"

    pmsg "Done removing environment files."
}
