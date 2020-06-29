#!/bin/bash

# import utilities
source "$fbrd/fb_cli/utils.sh"
source "$fbrd/orchestration/lockfile_utils.sh"

# parse inputs
experiment_name=$1
experiment_meta_identifier=$2
platform=$3
# if set to 'skip', code will not wait for experiment to finish
option=$4

# validate inputs
valid_platforms="aws_lambda azure_functions openfaas openfaas_eks"
# get valid experiment names
experiments=$(ls -I "*.md" "$fbrd/experiments")
# TODO fix check experiment
# if ! listContainsElement "$experiments" "$experiment_name"  ; then errmsg "Invalid experiment" ; exit 1 ; fi
if ! listContainsElement "$valid_platforms" "$platform" ; then errmsg "Invalid platform" ; exit 1 ; fi

# setup the local context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"

# =================================
# conditional variables
# =================================

# choose cloud function and clien provider based on platform input

case "$platform" in
    aws_lambda)
        experiment_cloud_function_provider="aws_lambda"
        experiment_client_provider="azure_linuxvm"
        experiment_client_env="$experiment_context/$experiment_name-azure_linuxvm.env"
        # check that infrastructure has been created
        check_lock "$experiment_name" "$experiment_client_provider" "infra" || exit
        check_lock "$experiment_name" "$experiment_cloud_function_provider" "infra" || exit
        ;;
    azure_functions)
        experiment_cloud_function_provider="azure_functions"
        experiment_client_provider="aws_ec2"
        experiment_client_env="$experiment_context/$experiment_name-aws_ec2.env"
        # check that infrastructure has been created
        check_lock "$experiment_name" "$experiment_client_provider" "infra" || exit
        check_lock "$experiment_name" "$experiment_cloud_function_provider" "infra" || exit
        ;;
    openfaas | openfaas_eks)
        experiment_client_provider="openfaas_client_vm"
        experiment_cloud_function_provider="openfaas"
        experiment_client_env="$experiment_context/$experiment_name-openfaas_client_vm.env"
        # check that infrastructure has been created
        check_lock "$experiment_name" "$experiment_client_provider" "infra" || exit
        ;;
esac

# =================================
# constants
# =================================

# the interval to check progress on client in seconds
check_progress_interval=300
# remote client user
client_user="ubuntu"
# user on db server
db_server_user="ubuntu"
# toggle development mode
dev_mode="False"
# print sql queries
verbose="False"
# path to the ssh key to connect to experiment client server
key_path="$fbrd/secrets/ssh_keys/experiment_servers"
# timestamp for when experiment execution started
timestamp=$(date -u +\"%d-%m-%Y_%H-%M-%S\")
# parse client server ip address from env file
client_ip=$(grep -oP "\d+\.\d+\.\d+\.\d+" $experiment_client_env)
# path of env file inside docker container on client server
docker_env_file_path="/home/docker/shared/$experiment_name-$experiment_cloud_function_provider.env"
# path to experiment python file inside docker container on experiment client server
docker_experiment_code_path="/home/docker/faas-benchmarker/experiments/$experiment_name/$experiment_name.py"
# name of experiment log file
logfile="/home/$client_user/$timestamp-$experiment_meta_identifier-$experiment_cloud_function_provider-$experiment_name.log"

# =================================
# compose ssh command
# =================================

docker_command="
    docker run \
        --rm \
        --mount type=bind,source=\"/home/$client_user\",target=\"/home/docker/shared\" \
        --mount type=bind,source=\"/home/$client_user/.ssh\",target=\"/home/docker/key\" \
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
    >> $logfile 2>&1"

experiment_failed_command="touch /home/$client_user/failed"

scp_logfile_command="scp -o StrictHostKeyChecking=no $logfile $db_server_user@\$DB_HOSTNAME:/home/$client_user/logs/experiments/"

scp_errorlog_command="[ -f \"/home/$client_user/ErrorLogFile.log\" ] && scp -o StrictHostKeyChecking=no /home/$client_user/ErrorLogFile.log \
    $db_server_user@\$DB_HOSTNAME:/home/$db_server_user/logs/error_logs/$timestamp-$experiment_meta_identifier-$experiment_client_provider-$experiment_name-ErrorLogFile.log"

create_done_file="touch /home/$client_user/done"

openfaas_eks_cluster_name="$experiment_name-$experiment_meta_identifier"
eks_bootstrap_command="bash \$fbrd/eks_openfaas_orchestration/bootstrap_openfaas_eks_fargate.sh $openfaas_eks_cluster_name >> $logfile 2>&1"
eks_destroy_command="bash \$fbrd/eks_openfaas_orchestration/teardown_openfaas_eks_fargate.sh $openfaas_eks_cluster_name >> $logfile 2>&1"

ssh_command="nohup bash -c '$docker_command || $experiment_failed_command ; $scp_logfile_command ; $scp_errorlog_command ; $create_done_file' >> /dev/null 2>&1 &"


# =================================
# check if experiment has finished
# =================================

function check_progress {
    if [ "$1" = "skip" ] ; then
        pmsg "Skipping wait for experiment."
    else
        pmsg "Now waiting for experiment to finish ..."
        until \
            ssh -o "StrictHostKeyChecking=no" -i "$key_path" "$client_user@$client_ip" "[ -f '/home/$client_user/done' ]" ; do
            echo "$(date) Waiting for experiment to finish ..."
            sleep $check_progress_interval
        done
    fi
}

# ======================================
# report if the experiment code failed
# ======================================

function check_if_experiment_failed {
    if ssh -o "StrictHostKeyChecking=no" -i "$key_path" "$client_user@$client_ip" "[ -f '/home/$client_user/failed' ]"
    then
        errmsg "Found failed indicator file, updating experiment status to failed ..."
        bash "$fbrd/orchestration/experiment_status_updater.sh" \
            "update_failed" \
            "$experiment_name" \
            "$experiment_meta_identifier" \
            "$experiment_cloud_function_provider" \
            "$experiment_client_provider"
        return 1
    else
        pmsg "Experiment process completed correctly ..."
        return 0
    fi
}

# ======================================
# openfaas helper functions
# ======================================

# TODO use
function check_eks_lockfile {
    eks_lockfile="$experiment_context/eks.lock"
    if [ -f "$eks_lockfile" ] ; then
        pmsg "Found eks lockfile ..."
        return 0
    else
        pmsg "Creating eks lockfile ..."
        touch "$eks_lockfile"
        return 1
    fi
}


# =================================
# execute experiment on server
# =================================

case "$platform" in

    aws_lambda | azure_functions)
        pmsg "Executing experiment code on remote client vm ..."

        # start the experiment process on the remote worker server
        ssh -o StrictHostKeyChecking=no -i $key_path $client_user@$client_ip $ssh_command

        # check every interval if the experiment code has finished running and the infrastructure can be destroyed
        check_progress "$option"

        # check if the file experiment process exited
        check_if_experiment_failed || exit

        smsg "Done executing experiment code."
        ;;

    openfaas)
        pmsg "Executing experiment code on remote client vm ..."

        ssh_command=""

        # TODO cleanup a bit more
        if [ "$option" = "bootstrap" ] ; then
            pmsg "Will only create the eks openfaas cluster ..."
            ssh_command="nohup bash -c '$eks_bootstrap_command' >> /dev/null 2>&1 &"
        elif [ "$option" = "destroy" ] ; then
            pmsg "Will only destroy the eks openfaas cluster ..."
            ssh_command="nohup bash -c '$eks_destroy_command' >> /dev/null 2>&1 &"
        elif [ "$option" = "run" ] ; then
            pmsg "Will run experiment, and wait for it to finish ..."
            ssh_command="nohup bash -c '$docker_command || $experiment_failed_command ; $scp_logfile_command ; $scp_errorlog_command ; $create_done_file' >> /dev/null 2>&1 &"
        elif [ "$option" = "skip" ] ; then
            pmsg "Will run experiment, and skip waiting for it to finish ..."
            ssh_command="nohup bash -c '$docker_command || $experiment_failed_command ; $scp_logfile_command ; $scp_errorlog_command ; $create_done_file' >> /dev/null 2>&1 &"
        else
            # this is the default behaviour used in production
            pmsg "Will bootstrap the openfaas eks cluster, run the experiment, wait for it to finish, then destroy the cluster ..."
            ssh_command="nohup bash -c ' $eks_bootstrap_command ; $docker_command || $experiment_failed_command ; $eks_destroy_command ; $scp_logfile_command ; $scp_errorlog_command ; $create_done_file' >> /dev/null 2>&1 &"
        fi

        # start the experiment process on the remote worker server
        ssh -o StrictHostKeyChecking=no -i $key_path $client_user@$client_ip $ssh_command

        if [ "$option" != 'bootstrap' ] && [ "$option" != "destroy" ] && [ "$option" != "skip" ] ; then
            # check every interval if the experiment code has finished running and the infrastructure can be destroyed
            check_progress "foo"
        fi

        # check if the file experiment process exited
        check_if_experiment_failed || exit

        smsg "Done executing experiment code."
        ;;


esac
