#!/bin/bash

# load helper functions
source $fbrd/fb_cli/utils.sh

# check that all dependencies are installed for running the local minikube cluster
function checkThatLocalDevDependenciesAreInstalled {
  [ ! -x "$(command -v minikube)" ] && echo "Please install minikube ..." && exit
  [ ! -x "$(command -v arkade)" ]   && echo "Please install arkade ..."   && exit
  [ ! -x "$(command -v faas-cli)" ] && echo "Please install faas-cli ..." && exit
  [ ! -x "$(command -v kubectl)" ]  && echo "Please install kubectl ..."  && exit
}

# create a local development environment using openfaas on minikube
function bootstrapOpenfaasLocally {
  checkThatLocalDevDependenciesAreInstalled
  bash "$fbrd/fb_cli/bootstrap_openfaas_locally.sh"
}

# destroy the created development environment
function teardownOpenfaasLocally {
  checkThatLocalDevDependenciesAreInstalled
  bash "$fbrd/fb_cli/teardown_openfaas_locally.sh"
}

function startMinikube {
  mkstatus=$(minikube status)
  if [[ $mkstatus =~ "There is no local cluster" ]] ; then
    pmsg "Openfaas has not been bootstrapped, creating now..."
    bootstrapOpenfaasLocally
  elif [[ $mkstatus =~ "host: Running" ]] ; then
    errmsg "Minikube is already running, will do nothing ..."
  elif [[ $mkstatus =~ "host: Stopped" ]] ; then
    pmsg "Starting minikube ..."
    minikube start
    pmsg "Starting port forward ..."
    kubectl port-forward -n openfaas svc/gateway 8080:8080 &
    echo
    smsg "OpenFaas on minikube ready for running experiments locally."
  fi
}

function fixMinikubePortForward {
  msg "Attempting to start port forwarding again ..."
  kubectl port-forward -n openfaas svc/gateway 8080:8080 &
  echo
}

function stopMinikube {
  pmsg "Stopping minikube ..."
  minikube stop
  pmsg "Stopping any lingering kubectl processes ..."
  killall -q kubectl
  smsg "Done stopping minikube."
}

function checkValidExperimentName {
  # get existing experiment names
  experiment_names=$(ls experiments)
  # check that name is unique
  echo "$experiment_names" | grep -qw "$1" && return 1
  # check that name is valid
  [[ "$1" =~ ^[a-zA-Z-]*$ ]] || return 1
  # return true if both checks are good
  return 0
}

function firstTimeInfrastrutureBootstrap {
  bash "$fbrd/fb_cli/first_time_infrasctructure_bootstrap.sh"
}

function destroyPermanentInfrastructure {
  bash "$fbrd/fb_cli/destroy_permanent_infrastructure.sh"
}

function sshOrchestrator {
  cd "$fbrd/infrastructure/orchestrator"
  ssh ubuntu@$(terraform output ip_address) -i ../../secrets/ssh_keys/orchestrator
  cd "$fbrd"
}

function sshDBServer {
  cd "$fbrd/infrastructure/db_server"
  ssh ubuntu@$(terraform output ip_address) -i ../../secrets/ssh_keys/db_server
  cd "$fbrd"
}

# create files for a new experiment from templates
function createExperiment {
  read -rp "New experiment name [a-zA-Z-]: " exp_name
  checkValidExperimentName "$exp_name" \
    && bash "$fbrd/fb_cli/create_experiment.sh" "$exp_name" \
    || ( errmsg "Invalid Experiment name ... aborting" && exit )
}

function listExperiments {
  ls -I "*.md" "$fbrd/experiments"
}

function chooseExperiment {
  experiments=$(listExperiments)
  experiments+=" cancel"
  select exp in $experiments ; do
    case "$exp" in
      # allow to go cancel
      cancel)
        echo ""
        break 1
        ;;

      # run an experiment
      *)
        echo $exp
        # go back to main menu after starting experiment
        break 1
        ;;
    esac
  done
}

# TODO
# function runExperiment {

# }

# TODO
function runExperimentLocally {
  pmsg "Running experiment: $1 locally with OpenFaas on Minikube ..."
  bash "$fbrd/fb_cli/run_experiment_local.sh" "$1"
}

# function reRunLastLocalExperiment {
# }

# ==================================

# check that all env vars are set
bash "$fbrd/fb_cli/check_env_vars.sh" && exit

# raise the banner...
cat "$fbrd/fb_cli/banner"

# commands that can be issued
options="
run_experiment
run_all_experiments
generate_graphs
create_experiment
first_time_infrastructure_bootstrap
destroy_permanent_infrastructure
dev_options
"

# add ssh commands if not on orchestrator server
if [ "$HOSTNAME" != "orchestrator" ] ; then
  options+=" ssh_orchestrator ssh_db_server"
fi

# make sure exit is always the last option...
options+=" exit"

dev_options="
run_experiment_locally
fix_minikube_port_forward
start_minikube
stop_minikube
minikube_status
bootstrap_openfaas_locally
teardown_openfaas_locally
main_menu
"

# interactively choose command
select opt in $options; do
  case "$opt" in

    run_experiment)
      exp=$(chooseExperiment)

      # break out if cancelled
      [ -z "$exp" ] && msg "Cancelled." && break 1

      echo "you chose $exp"
      ;;

    run_all_experiments)
      # TODO
      echo "not implemented yet"
      ;;

    generate_graphs)
      # TODO
      echo "not implemented yet"
      ;;

    create_experiment)
      createExperiment
      ;;

    first_time_infrastructure_bootstrap)
      firstTimeInfrastrutureBootstrap
      ;;

    destroy_permanent_infrastructure)
      destroyPermanentInfrastructure
      ;;

    ssh_orchestrator)
      sshOrchestrator
      ;;

    ssh_db_server)
      sshDBServer
      ;;

    dev_options)
      echo "Options for running experiments locally for development:"
      select dev_opt in $dev_options ; do
        case $dev_opt in

          run_experiment_locally)
            dev_exp=$(chooseExperiment)

            # break out if cancelled
            [ -z "$dev_exp" ] && msg "Cancelled." && break 1

            runExperimentLocally "$dev_exp"
            ;;

          fix_minikube_port_forward)
            fixMinikubePortForward
            ;;

          start_minikube)
            startMinikube
            ;;

          stop_minikube)
            stopMinikube
            ;;

          minikube_status)
            minikube status
            ;;

          bootstrap_openfaas_locally)
            bootstrapOpenfaasLocally
            ;;

          teardown_openfaas_locally)
            teardownOpenfaasLocally
            ;;

          # go back to previous menu
          main_menu)
            break 1
            ;;

          *)
            echo "Press return to see options ..."
            ;;

        esac
      done
      ;;

    exit)
      exit
      ;;

    *)
      echo "Press return to see options ..."
      ;;

  esac
done
