#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

# provision infrastructure, run experiment code and then destroy infrastructure

# the experiment name to test
experiment_name=$1
# unique experiment idenfifier for the experiments started in parallel for the different cloud providers
experiment_meta_identifier=$2
# the context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"
# the experiemnt logic file
experiment_python_file="$fbrd/experiments/$experiment_name/$experiment_name.py"
# which cloud function
experiment_cloud_function_provider="azure_functions"
# which client vm
experiment_client_provider="aws_ec2"
# env vars for the cloud functions
experiment_cloud_function_env="$experiment_context/$experiment_name-azure_functions.env"
# env vars for the client vm
experiment_client_env="$experiment_context/$experiment_name-aws_ec2.env"
# where the env file should be placed on the client
remote_env_file="/home/ubuntu/$experiment_name-azure_functions.env"

# remote faas-benchmarker directory location
remote_fbrd="/home/ubuntu/faas-benchmarker"

# the interval to check progress on client in seconds
check_progress_interval=600

# ===== create cloud functions

cd "$experiment_context/azure_functions"

pmsg "Initializing terraform ..."
bash init.sh "$experiment_name"

pmsg "Creating cloud functions ..."
terraform apply -auto-approve

pmsg "Fixing broken terraform azure function code deployment ..."

# reupload function code but with dependencies....
function_code_dirs=$(ls function_code/)
for fcd in $function_code_dirs; do
    # get the function number
    fx_num=$(echo $fcd | grep -oP "\d")
    exp_function_app_name=$experiment_name$fx_num-python
    cd function_code/$fcd
    func azure functionapp publish $exp_function_app_name
    cd ../..
done

pmsg "Outputting variables to $experiment_name-awslambda.env ..."
terraform output > "$experiment_cloud_function_env"

smsg "Done creating cloud functions."

# ===== create client vm

cd "$experiment_context/aws_ec2"

pmsg "Initializing terraform ..."
bash init.sh "$experiment_name"

pmsg "Creating client vm ..."
terraform apply \
    -auto-approve \
    -var "env_file=$experiment_cloud_function_env" \
    -var "remote_env_file=$remote_env_file"

pmsg "Outputting variables to $experiment_name-aws_ec2.env ..."
terraform output > "$experiment_client_env"

smsg "Done creating client vm."

# ===== run experiment code

pmsg "Executing experiment code on remote client vm ..."

cd "$experiment_context"

client_user="ubuntu"
client_ip=$(grep -oP "\d+\.\d+\.\d+\.\d+" $experiment_client_env)
key_path="$fbrd/secrets/ssh_keys/experiment_servers"
timestamp=$(date -u +\"%d-%m-%Y_%H-%M-%S\")
logfile="/home/ubuntu/$timestamp-$experiment_meta_identifier-$experiment_cloud_function_provider-$experiment_name.log"
docker_experiment_code_path="/home/docker/faas-benchmarker/experiments/$experiment_name/$experiment_name.py"
docker_env_file_path="/home/docker/shared/$experiment_name-$experiment_cloud_function_provider.env"
ssh_command="
    nohup bash -c ' \
        docker run \
            --rm \
            --mount type=bind,source=\"/home/ubuntu\",target=\"/home/docker/shared\" \
            --mount type=bind,source=\"/home/ubuntu/.ssh\",target=\"/home/docker/.ssh\" \
            -e \"DB_HOSTNAME=$DB_HOSTNAME\" \
            --network host \
            faasbenchmarker/client:latest \
            python \
            $docker_experiment_code_path \
            $experiment_name \
            $experiment_meta_identifier \
            $experiment_cloud_function_provider \
            $experiment_client_provider \
            $docker_env_file_path
        > $logfile 2>&1
        ; scp -o StrictHostKeyChecking=no $logfile ubuntu@\$DB_HOSTNAME:/home/ubuntu/logs/experiments/
        ; [ -f \"/home/ubuntu/ErrorLogFile.log\" ] && scp -o StrictHostKeyChecking=no /home/ubuntu/ErrorLogFile.log \
            ubuntu@\$DB_HOSTNAME:/home/ubuntu/logs/error_logs/$timestamp-$experiment_client_provider-$experiment_name-ErrorLogFile.log
        ; touch /home/ubuntu/done
    ' > /dev/null & "

ssh -o StrictHostKeyChecking=no -i $key_path $client_user@$client_ip $ssh_command

# check every interval if the experiment code has finished running and the infrastructure can be destroyed
until ssh -o "StrictHostKeyChecking=no" -i "$key_path" "$client_user@$client_ip" "[ -f '/home/ubuntu/done' ]" ; do
    echo "$(date) Waiting for experiment to finish ..."
    sleep $check_progress_interval
done

smsg "Done executing experiment code."

# ===== destroy cloud functions

cd "$experiment_context/$experiment_cloud_function_provider"

pmsg "Destroying cloud functions ..."

terraform destroy -auto-approve
# azure sometimes needs a little persuasions to actually destroy everything...
# so we do it again just to be sure ...
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
