#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

set -e

[ -z "$1" ] && errmsg "Please specify experiment name as first argument." && exit
experiment_name=$1
cluster_name="$experiment_name-openfaas-cluster"
region="eu-west-1"

pmsg "Destroying OpenFaas on AWS EKS/Fargate ..."
pmsg "Experiment name: $experiment_name"
pmsg "EKS cluster name: $cluster_name"
pmsg "AWS region: $region"

pmsg "Removing deployed OpenFaas functions ..."

faas-cli remove -f $fbrd/cloud_functions/openfaas/faas_benchmarker_functions.yml

pmsg "Destroying EKS cluster ..."

eksctl delete cluster \
    --name "$cluster_name" \
    --region "$region"

smsg "Done destroying OpenFaas infrastructure."
