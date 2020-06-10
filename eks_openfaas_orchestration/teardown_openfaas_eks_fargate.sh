#!/bin/bash

set -e

[ -z "$1" ] && errmsg "Please specify experiment name as first argument." && exit
experiment_name=$1
cluster_name="$experiment_name-openfaas-cluster"
region="eu-west-1"

pmsg "\nDestroying OpenFaas on AWS EKS/Fargate ..."
pmsg "Experiment name: $experiment_name"
pmsg "EKS cluster name: $cluster_name"
pmsg "AWS region: $region\n"

pmsg "\nRemoving deployed OpenFaas functions ...\n"

faas-cli remove -f $fbrd/cloud_functions/openfaas/faas_benchmarker_functions.yml

pmsg "\nDestroying EKS cluster ...\n"

eksctl delete cluster \
    --name "$cluster_name" \
    --region "$region"

smsg "\nDone destroying OpenFaas infrastructure.\n"
