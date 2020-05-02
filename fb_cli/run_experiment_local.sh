#!/bin/bash

# the experiment name to test
experiment_name=$1
# the context of the experiment
experiment_context="$fbrd/experiments/$experiment_name"
# the experiemnt logic file
experiment_python_file="$experiment_context/$experiment_name.py"
# we test locally againt minikube
experiment_cloud_function_provider="openfaas"
# we do not need an env file for openfaas on minikube
experiment_env_file="$experiment_context/$experiment_name.env"
# dev_mode
dev_mode="True"

python \
  $experiment_python_file \
  $experiment_name \
  $experiment_cloud_function_provider \
  $experiment_env_file \
  $dev_mode
