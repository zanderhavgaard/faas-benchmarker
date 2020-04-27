#!/bin/bash

banner=$(cat << EOB
  __ _                _ _
 / _| |__         ___| (_)
| |_| '_ \ _____ / __| | |
|  _| |_) |_____| (__| | |
|_| |_.__/       \___|_|_|
EOB
)

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

# ==================================

# check that all env vars are set
bash "$fbrd/fb_cli/check_env_vars.sh" && exit

# raise the banner...
echo "$banner"

# commands that can be issued
options="
run_experiment
run_all_experiments
generate_graphs
create_experiment
first_time_infrastructure_bootstrap
dev_options
exit
"

dev_options="
run_experiment_locally
bootstrap_openfaas_locally
teardown_openfaas_locally
main_menu
"

# interactively choose command
select opt in $options; do
  case "$opt" in

    run_experiment)
      echo "not implemented yet"
      ;;

    run_all_experiments)
      echo "not implemented yet"
      ;;

    generate_graphs)
      echo "not implemented yet"
      ;;

    create_experiment)
      echo "not implemented yet"
      ;;

    first_time_infrastructure_bootstrap)
      echo "not implemented yet"
      ;;

    dev_options)
      echo "Options for running experiments locally for development:"
      select dev_opt in $dev_options ; do
        case $dev_opt in

          run_experiment_locally)
            echo "not implemented yet"
            ;;

          bootstrap_openfaas_locally)
            bootstrapOpenfaasLocally
            ;;

          teardown_openfaas_locally)
            teardownOpenfaasLocally
            ;;

          # go back to previose menu
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
