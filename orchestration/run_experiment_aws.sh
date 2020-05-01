#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

# provision infrastructure, run experiment code and then destroy infrastructure

# the experiment name to test
experiment_name=$1
# the context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"
# the experiemnt logic file
experiment_python_file="$experiment_context/$experiment_name.py"
# which cloud function
experiment_cloud_function_provider="aws_lambda"
# which client vm
experiment_client_provider="azure_linuxvm"
# env vars for the cloud functions
experiment_cloud_function_env_var="$experiment_context/$experiment_name-aws_lambda.env"
# env vars for the client vm
experiment_client_env_var="$experiment_context/$experiment_name-azure_linuxvm.env"
# where the env file should be placed on the client
remote_env_file="/home/ubuntu/faas-benchmarker/experiments/$experiment_name/$experiment_name-awslambda.env"

# ===== create cloud functions

cd "$experiment_context/aws_lambda"

pmsg "Initializing terraform ..."
bash init.sh "$experiment_name"

pmsg "Creating cloud functions ..."
terraform apply -auto-approve

# echo -e "\n--> Outputting variables to experiment.env ...\n"
pmsg "Outputting variables to $experiment_name-awslambda.env ..."
terraform output > "$experiment_cloud_function_env_var"

smsg "Done creating cloud functions."

# ===== create client vm

cd "$experiment_context/azure_linuxvm"

pmsg "Initializing terraform ..."
bash init.sh "$experiment_name"

pmsg "Creating client vm ..."
terraform apply \
    -auto-approve \
    -var "env_file=$experiment_cloud_function_env_var" \
    -var "remote_env_file=$remote_env_file"

pmsg "Outputting variables to $experiment_name-azure_linuxvm.env ..."
terraform output > "$experiment_client_env_var"

smsg "Done creating client vm."

# ===== run experiment code

# cd "$experiment_context"

# client_user="ubuntu"
# client_ip=$(grep -oP "\d+\.\d+\.\d+\.\d+" $experiment_client_env_var)
# key_path="$fbrd/secrets/ssh_keys/experiment_servers"
# # $fbrd will expanded on the client, the rest will be expanded locally!
# ssh_command="cd \$fbrd/experiments/$experiment_context && python3 \$fbrd/experiments/$experiment_context/$experiment_code $experiment_name"
# ssh -o StrictHostKeyChecking=no -i $key_path $client_user@$client_ip $ssh_command
