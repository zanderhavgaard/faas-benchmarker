#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

command=$1
experiment_name=$2
experiment_meta_identifier=$3
function_provider=$4
client_provider=$5

docker_cmd="docker run --rm --network host mysql:5.7 mysql -uroot -pfaas -h127.0.0.1 -P3306 Benchmarks -e"

case "$command" in
    insert)
        pmsg "Inserting new ExperimentStatus row ..."
        experiment_status="running"
        ssh_command="ubuntu@68.183.243.126"
        ssh $ssh_command " docker run --rm --network host mysql:5.7 mysql -uroot -pfaas -h127.0.0.1 -P3306 Benchmarks -e \" insert into ExperimentStatus (name, experiment_meta_identifier, function_provider, client_provider, status) values ('$experiment_name', '$experiment_meta_identifier', '$function_provider', '$client_provider', '$experiment_status') ;  \" "
        ;;
    update_finished)
        pmsg "Updating ExperimentStatus row to completed ..."
        ;;
    update_failed)
        pmsg "Updaeting ExperimentStatus row to failed ..."
        ;;
    *)
        errmsg "Invalid command, valid commands are: insert, update_finished, update_failed"
        ;;
esac
