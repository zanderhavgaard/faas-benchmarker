#!/bin/bash

set -e

[ -z "$1" ] && echo "Please specify experiment name as first argument." && exit
experiment_name=$1
cluster_name="$experiment_name-openfaas-cluster"
region="eu-west-1"

echo -e "\nDestroying OpenFaas on AWS EKS/Fargate ..."
echo -e "Experiment name: $experiment_name"
echo -e "EKS cluster name: $cluster_name"
echo -e "AWS region: $region\n"

echo -e "\nRemoving deployed OpenFaas functions ...\n"

faas-cli remove -f $fbrd/cloud_functions/openfaas/faas_benchmarker_functions.yml

echo -e "\nDestroying EKS cluster ...\n"

eksctl delete cluster \
    --name "$cluster_name" \
    --region "$region"

echo -e "\nDone destroying OpenFaas infrastructure.\n"
