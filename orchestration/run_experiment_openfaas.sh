#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

# provision infrastructure, run experiment code and then destroy infrastructure

# the experiment name to test
experiment_name=$1
# the context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"
# the experiemnt logic file
experiment_python_file="$fbrd/experiments/$experiment_name/$experiment_name.py"
# which client vm
experiment_client_provider="openfaas_client_vm"
# which cloud function provider
experiment_cloud_function_provider="openfaas"
# env vars for the client vm
experiment_client_env="$experiment_context/$experiment_name-openfaas_client_vm.env"

# remote faas-benchmarker directory location
remote_fbrd="/home/ubuntu/faas-benchmarker"

# the interval to check progress on client in seconds
check_progress_interval=600


# ===== create client vm

cd "$experiment_context/openfaas_client_vm"

pmsg "Initializing terraform ..."
bash init.sh "$experiment_name"

pmsg "Creating client vm ..."
terraform apply \
    -auto-approve

pmsg "Outputting variables to $experiment_name-openfaas_client.env ..."
terraform output > "$experiment_client_env"

smsg "Done creating client vm."

# ===== run experiment code

pmsg "Executing experiment code on remote client vm ..."

cd "$experiment_context"

client_user="ubuntu"
client_ip=$(grep -oP "\d+\.\d+\.\d+\.\d+" $experiment_client_env)
key_path="$fbrd/secrets/ssh_keys/experiment_servers"
timestamp=$(date -u +\"%d-%m-%Y_%H-%M-%S\")
logfile="~/$experiment_name-$timestamp.log"
# $fbrd will expanded on the client, the rest will be expanded locally!
ssh_command="
    nohup bash -c ' \
    bash \$fbrd/eks_openfaas_orchestration/bootstrap_openfaas_eks_fargate.sh $experiment_name >> $logfile 2>&1
    ; python3 \$fbrd/experiments/$experiment_name/$experiment_name.py \
    $experiment_name \
    $experiment_cloud_function_provider \
    'openfaas-does-not-need-an-env-file' \
    >> $logfile 2>&1
    ; bash \$fbrd/eks_openfaas_orchestration/teardown_openfaas_eks_fargate.sh $experiment_name >> $logfile 2>&1
    ; scp -o StrictHostKeyChecking=no $logfile ubuntu@\$DB_HOSTNAME:/home/ubuntu/logs/experiments/
    ; touch /home/ubuntu/done
    ' > /dev/null & "

# start the experiment process on the remote worker server
ssh -o StrictHostKeyChecking=no -i $key_path $client_user@$client_ip $ssh_command

# check every interval if the experiment code has finished running and the infrastructure can be destroyed
until ssh -o "StrictHostKeyChecking=no" -i "$key_path" "$client_user@$client_ip" "[ -f '/home/ubuntu/done' ]" ; do
    echo "$(date) Waiting for experiment to finish ..."
    sleep $check_progress_interval
done

smsg "Done executing experiment code."

# ===== destroy client vm

cd "$experiment_context/$experiment_client_provider"

pmsg "Destroying client vm ..."

terraform destroy \
    -auto-approve

smsg "Done destroying client vm."

# ===== remove experiment env files

pmsg "Removing experiment environment files ..."

rm "$experiment_client_env"

smsg "Done removing environment files."
