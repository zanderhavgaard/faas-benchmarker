
function run {
    experiment_name=$1
    experiment_meta_identifier=$2
    experiment_context="$fbrd/experiments/$experiment_name"
    experiment_cloud_function_env="$experiment_context/$experiment_name-aws_lambda.env"
    experiment_client_env="$experiment_context/$experiment_name-azure_linuxvm.env"

    pmsg "Executing experiment code on remote client vm ..."

    cd "$experiment_context"

    client_user="ubuntu"
    client_ip=$(grep -oP "\d+\.\d+\.\d+\.\d+" $experiment_client_env)
    key_path="$fbrd/secrets/ssh_keys/experiment_servers"
    timestamp=$(date -u +\"%d-%m-%Y_%H-%M-%S\")
    logfile="/home/ubuntu/$timestamp-$experiment_meta_identifier-$experiment_cloud_function_provider-$experiment_name.log"
    docker_experiment_code_path="/home/docker/faas-benchmarker/experiments/$experiment_name/$experiment_name.py"
    docker_env_file_path="/home/docker/shared/$experiment_name-$experiment_cloud_function_provider.env"
    dev_mode="False"
    verbose="False"
    ssh_command="
        nohup bash -c ' \
            docker run \
                --rm \
                --mount type=bind,source=\"/home/ubuntu\",target=\"/home/docker/shared\" \
                --mount type=bind,source=\"/home/ubuntu/.ssh\",target=\"/home/docker/key\" \
                -e \"DB_HOSTNAME=\$DB_HOSTNAME\" \
                --network host \
                faasbenchmarker/client:latest \
                python \
                $docker_experiment_code_path \
                $experiment_name \
                $experiment_meta_identifier \
                $experiment_cloud_function_provider \
                $experiment_client_provider \
                $docker_env_file_path \
                $dev_mode \
                $verbose
            >> $logfile 2>&1
            ; scp -o StrictHostKeyChecking=no $logfile ubuntu@\$DB_HOSTNAME:/home/ubuntu/logs/experiments/
            ; [ -f \"/home/ubuntu/ErrorLogFile.log\" ] && scp -o StrictHostKeyChecking=no /home/ubuntu/ErrorLogFile.log \
                ubuntu@\$DB_HOSTNAME:/home/ubuntu/logs/error_logs/$timestamp-$experiment_meta_identifier-$experiment_client_provider-$experiment_name-ErrorLogFile.log
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
}
