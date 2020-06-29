#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

command=$1
experiment_name=$2
experiment_meta_identifier=$3
function_provider=$4
client_provider=$5

ssh_command="ubuntu@$TF_VAR_db_server_static_ip"

case "$command" in

    insert)
        start_time=$(date +%s)
        pmsg "Inserting new ExperimentStatus row ..."
        experiment_status="running"
        ssh $ssh_command " docker run --rm --network host mysql:5.7 mysql -uroot -pfaas -h127.0.0.1 -P3306 Benchmarks -e \" insert into ExperimentStatus (name, experiment_meta_identifier, function_provider, client_provider, start_time, status) values ('$experiment_name', '$experiment_meta_identifier', '$function_provider', '$client_provider', '$start_time', '$experiment_status') ;  \" "
        ;;


    update_completed)
        end_time=$(date +%s)
        # pmsg "Updating ExperimentStatus row to completed ..."
        experiment_status="completed"
        status=$(ssh $ssh_command " docker run --rm --network host mysql:5.7 mysql -uroot -pfaas -h127.0.0.1 -P3306 Benchmarks -e \" select status from ExperimentStatus where name='$experiment_name' and experiment_meta_identifier='$experiment_meta_identifier' and function_provider='$function_provider' and client_provider='$client_provider' ;  \" ")
        if [[ "$status" =~ "running" ]] ; then
            pmsg "Found ExperimentStatus row, updating to completed ..."
            ssh $ssh_command " docker run --rm --network host mysql:5.7 mysql -uroot -pfaas -h127.0.0.1 -P3306 Benchmarks -e \" update ExperimentStatus set status='$experiment_status', end_time='$end_time' where name='$experiment_name' and experiment_meta_identifier='$experiment_meta_identifier' and function_provider='$function_provider' and client_provider='$client_provider' ;  \" "
        elif [[ "$status" =~ "failed" ]] ; then
            pmsg "Experiment has already been marked failed, will only update end_time ..."
            ssh $ssh_command " docker run --rm --network host mysql:5.7 mysql -uroot -pfaas -h127.0.0.1 -P3306 Benchmarks -e \" update ExperimentStatus set end_time='$end_time' where name='$experiment_name' and experiment_meta_identifier='$experiment_meta_identifier' and function_provider='$function_provider' and client_provider='$client_provider' ;  \" "
        fi

        ;;


    update_failed)
        end_time=$(date +%s)
        pmsg "Updating ExperimentStatus row to failed ..."
        experiment_status="failed"
        ssh $ssh_command " docker run --rm --network host mysql:5.7 mysql -uroot -pfaas -h127.0.0.1 -P3306 Benchmarks -e \" update ExperimentStatus set status='$experiment_status', end_time='$end_time' where name='$experiment_name' and experiment_meta_identifier='$experiment_meta_identifier' and function_provider='$function_provider' and client_provider='$client_provider' ;  \" "
        ;;


    *)
        errmsg "Invalid command, valid commands are: insert, update_finished, update_failed"
        ;;
esac
