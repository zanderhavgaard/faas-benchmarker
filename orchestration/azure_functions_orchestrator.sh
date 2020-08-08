#!/bin/bash

# remove flag as it conflicts with the until loop
# set -e

source "$fbrd/fb_cli/utils.sh"

function bootstrap {
    experiment_name=$1
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_cloud_function_env="$experiment_context/$experiment_name-azure_functions.env"

    cd "$experiment_context/azure_functions"

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

    pmsg "Outputting variables to $experiment_name-azure_functions.env ..."
    terraform output > "$experiment_cloud_function_env"

    pmsg "Fixing broken terraform azure function code deployment ..."

    # reupload function code but with dependencies....
    function_code_dirs=$(ls function_code/)
    for fcd in $function_code_dirs; do
        pmsg "Fixing deployment of azure function: $fcd"
        cd "$experiment_context/azure_functions/function_code/$fcd"

        # we retry the function app publish, as it might fail...
        retries=20
        counter=0
        deployed="false"
        delay=60
        until $deployed ; do
            (( counter++ ))
            if [ $counter = $retries ] ; then
                errmsg "Maximum deployment retries reached, aborting ..."
                exit
            fi
            pmsg "Trying functionapp deployment, attempt # $counter / $retries ..."
            func azure functionapp publish $fcd

            # verify that the function was actually deployed correctly ...........
            cd "$experiment_context/azure_functions/"
            pmsg "attempting to invoke function ..."
            curl -f -d '{}' "$(terraform output ${fcd}_function_app_url)/api/$fcd?code=$(terraform output ${fcd}_function_key)" \
                && deployed="true"
            cd "$experiment_context/azure_functions/function_code/$fcd"

            if ! $deployed ; then
                pmsg "Deployment failed, sleeping for $delay seconds, and will try again ..."
                sleep $delay
            else
                smsg "Successfully deployed function $fcd"
            fi

        done
    done

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

    rm -f "$experiment_cloud_function_env"

    pmsg "Done removing environment files."
}
