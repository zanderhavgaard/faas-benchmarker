#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

# set might mess with the until loop
# set -e

[ -z "$1" ] && errmsg "Please specify experiment name as first argument." && exit 1
experiment_name=$1
cluster_name="$experiment_name-openfaas-cluster"
region="eu-west-1"

pmsg "Bootstrapping OpenFaas on AWS EKS/Fargate ..."
pmsg "Experiment name: $experiment_name"
pmsg "EKS cluster name: $cluster_name"
pmsg "AWS region: $region"

pmsg "Creating EKS cluster on fargate ..."

# create the cluster
eksctl create cluster \
    --fargate \
    --name "$cluster_name" \
    --region "$region" \

# wait a bit for things to be ready
sleep 5

pmsg "Creating fargateprofile for openfaas namespace ..."

# setup fargate profiles for namespaces
eksctl create fargateprofile \
    --cluster "$cluster_name" \
    --region "$region" \
    --namespace openfaas

# wait a bit for things to be ready
sleep 5

pmsg "Creating fargateprofile for openfaas-fn namespace ..."

eksctl create fargateprofile \
    --cluster "$cluster_name" \
    --region "$region" \
    --namespace openfaas-fn

# wait a bit for things to be ready
sleep 5

pmsg "arkade install openfaas ..."

# the arkade install might fail, so we try a few times ...
retries=10
counter=0
deployed="false"
until $deployed ; do
    (( counter++ ))
    if [ $counter = $retries ] ; then
        errmsg "Maximum deployment retries reached, aborting ..."
        exit
    fi
    pmsg "Trying openfaas deployment, attempt # $counter..."
    # install openfaas
    arkade install openfaas \
        --wait \
        --load-balancer \
        --set "faasIdler.dryRun=false" \
        --set "faasIdler.inactivityDuration=30m" \
        --set "faasIdler.reconcileInterval=10m" \
        && deployed="true" \
        && smsg "Successfully deployed openfaas $fcd"
done

# wait a bit for things to be ready
sleep 5

pmsg "Kubectl openfaas gateway rollout ..."

# configure openfaas
kubectl rollout status -n openfaas deploy/gateway

sleep 5

pmsg "Creating portforwarding ..."

kubectl port-forward -n openfaas svc/gateway 8080:8080 &

# wait a bit for things to be ready
sleep 5

pmsg "faas-cli log in to cluste ..."

# log faas-cli into the new cluster
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

pmsg "Pulling OpenFaas template files ..."

# download openfaas template files
faas-cli template pull

pmsg "Deploying functions ..."

# deploy the functions
faas-cli deploy \
  -f $fbrd/cloud_functions/openfaas/faas_benchmarker_functions.yml \
  --label "com.openfaas.scale.zero=true"

smsg "Done configuring OpenFaas"
