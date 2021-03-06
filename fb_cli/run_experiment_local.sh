#!/bin/bash

# the experiment name to test
experiment_name=$1
# meta identifier
experiment_meta_identifier="dev-meta"
# the context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"
# the experiemnt logic file
experiment_python_file="$experiment_context/$experiment_name.py"
# we test locally againt minikube
experiment_cloud_function_provider="openfaas"
# experiment_cloud_function_provider="aws_lambda"
# experiment_cloud_function_provider="azure_functions"
# client is the dev machine
experiment_client_provider="dev"
# we do not need an env file for openfaas on minikube
experiment_env_file="$experiment_context/$experiment_name.env"
# dev_mode
dev_mode="True"
# more detailed print
verbose="False"

python \
  $experiment_python_file \
  $experiment_name \
  $experiment_meta_identifier \
  $experiment_cloud_function_provider \
  $experiment_client_provider \
  $experiment_env_file \
  $dev_mode \
  $verbose
