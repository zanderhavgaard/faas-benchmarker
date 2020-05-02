#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

# provision infrastructure, run experiment code and then destroy infrastructure

# the experiment name to test
experiment_name=$1
# the context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"
# the experiemnt logic file
experiment_python_file="$fbrd/experiments/$experiment_name/$experiment_name.py"
# which cloud function
experiment_cloud_function_provider="aws_lambda"
# which client vm
experiment_client_provider="azure_linuxvm"
# env vars for the cloud functions
experiment_cloud_function_env="$experiment_context/$experiment_name-aws_lambda.env"
# env vars for the client vm
experiment_client_env="$experiment_context/$experiment_name-azure_linuxvm.env"
# where the env file should be placed on the client
remote_env_file="/home/ubuntu/faas-benchmarker/experiments/$experiment_name/$experiment_name-awslambda.env"

# remote faas-benchmarker directory location
remote_fbrd="/home/ubuntu/faas-benchmarker"

# ===== create cloud functions

# cd "$experiment_context/aws_lambda"

# pmsg "Initializing terraform ..."
# bash init.sh "$experiment_name"

# pmsg "Creating cloud functions ..."
# terraform apply -auto-approve

# # echo -e "\n--> Outputting variables to experiment.env ...\n"
# pmsg "Outputting variables to $experiment_name-awslambda.env ..."
# terraform output > "$experiment_cloud_function_env"

# smsg "Done creating cloud functions."

# ===== create client vm

# cd "$experiment_context/azure_linuxvm"

# pmsg "Initializing terraform ..."
# bash init.sh "$experiment_name"

# pmsg "Creating client vm ..."
# terraform apply \
    # -auto-approve \
    # -var "env_file=$experiment_cloud_function_env" \
    # -var "remote_env_file=$remote_env_file"

# pmsg "Outputting variables to $experiment_name-azure_linuxvm.env ..."
# terraform output > "$experiment_client_env"

# smsg "Done creating client vm."

# ===== run experiment code

# pmsg "Executing experiment code on remote client vm ..."

# cd "$experiment_context"

# client_user="ubuntu"
# client_ip=$(grep -oP "\d+\.\d+\.\d+\.\d+" $experiment_client_env)
# key_path="$fbrd/secrets/ssh_keys/experiment_servers"
# # $fbrd will expanded on the client, the rest will be expanded locally!
# ssh_command="nohup \
    # python3 $remote_fbrd/experiments/$experiment_name/$experiment_name.py \
    # $experiment_name \
    # $experiment_cloud_function_provider \
    # $remote_fbrd/experiments/$experiment_name/$experiment_name-$experiment_cloud_function_provider.env \
    # > ~/$experiment_name-\$(date -u +\"%d-%m-%Y_%H:%M:%S\").log 2>&1
    # "

# ssh -o StrictHostKeyChecking=no -i $key_path $client_user@$client_ip $ssh_command

# smsg "Done executing experiment code."

# ===== destroy cloud functions

cd "$experiment_context/$experiment_cloud_function_provider"

pmsg "Destroying cloud functions ..."

terraform destroy -auto-approve

smsg "Done destroying cloud functions."

# ===== destroy client vm

cd "$experiment_context/$experiment_client_provider"

pmsg "Destroying client vm ..."

terraform destroy \
    -auto-approve \
    -var "env_file=$experiment_cloud_function_env" \
    -var "remote_env_file=$remote_env_file"

smsg "Done destroying client vm."

# ===== remove experiment env files

pmsg "Removing experiment environment files ..."

rm "$experiment_cloud_function_env" "$experiment_client_env"

smsg "Done removing environment files."















#
