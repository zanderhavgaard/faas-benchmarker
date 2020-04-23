#!/bin/bash

set -e

[ -z "$1" ] && echo "Please specify experiment name as first argument." && exit
experiment_name=$1
cluster_name="$experiment_name-openfaas-cluster"
region="eu-west-1"

echo -e "\nBootstrapping OpenFaas on AWS EKS/Fargate ..."
echo -e "Experiment name: $experiment_name"
echo -e "EKS cluster name: $cluster_name"
echo -e "AWS region: $region\n"

# create the cluster
eksctl create cluster \
    --fargate \
    --name "$cluster_name" \
    --region "$region" \

# wait a bit for things to be ready
sleep 5

# setup fargate profiles for namespaces
eksctl create fargateprofile \
    --cluster "$cluster_name" \
    --region "$region" \
    --namespace openfaas

# wait a bit for things to be ready
sleep 5

eksctl create fargateprofile \
    --cluster "$cluster_name" \
    --region "$region" \
    --namespace openfaas-fn

# wait a bit for things to be ready
sleep 5

# install openfaas
arkade install openfaas --load-balancer

# wait a bit for things to be ready
sleep 5

# configure openfaas
kubectl rollout status -n openfaas deploy/gateway
kubectl port-forward -n openfaas svc/gateway 8080:8080 &

# wait a bit for things to be ready
sleep 5

# log faas-cli into the new cluster
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

# download openfaas template files
faas-cli template pull

# deploy the functions
faas-cli deploy -f $fbrd/cloud_functions/openfaas/faas_benchmarker_functions.yml

echo -e "\nDone configuring OpenFaas\n"
