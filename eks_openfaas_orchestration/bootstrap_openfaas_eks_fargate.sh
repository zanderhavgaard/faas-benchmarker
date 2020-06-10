#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

# set might mess with the until loop
# set -e

[ -z "$1" ] && errmsg "Please specify experiment name as first argument." && exit 1
experiment_name=$1
cluster_name="$experiment_name-openfaas-cluster"
region="eu-west-1"

pmsg -e "\nBootstrapping OpenFaas on AWS EKS/Fargate ..."
pmsg -e "Experiment name: $experiment_name"
pmsg -e "EKS cluster name: $cluster_name"
pmsg -e "AWS region: $region\n"

pmsg -e "\n--> Creating EKS cluster on fargate ...\n"

# create the cluster
eksctl create cluster \
    --fargate \
    --name "$cluster_name" \
    --region "$region" \

# wait a bit for things to be ready
sleep 5

pmsg -e "\n--> Creating fargateprofile for openfaas namespace ...\n"

# setup fargate profiles for namespaces
eksctl create fargateprofile \
    --cluster "$cluster_name" \
    --region "$region" \
    --namespace openfaas

# wait a bit for things to be ready
sleep 5

pmsg -e "\n--> Creating fargateprofile for openfaas-fn namespace ...\n"

eksctl create fargateprofile \
    --cluster "$cluster_name" \
    --region "$region" \
    --namespace openfaas-fn

# wait a bit for things to be ready
sleep 5

pmsg -e "\n--> arkade install openfaas ...\n"

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

pmsg -e "\n--> Kubectl openfaas gateway rollout ...\n"

# configure openfaas
kubectl rollout status -n openfaas deploy/gateway

sleep 5

pmsg -e "\n--> Creating portforwarding ...\n"

kubectl port-forward -n openfaas svc/gateway 8080:8080 &

# wait a bit for things to be ready
sleep 5

pmsg -e "\n--> faas-cli log in to cluste ...\n"

# log faas-cli into the new cluster
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

pmsg -e "\n--> Pulling OpenFaas template files ...\n"

# download openfaas template files
faas-cli template pull

pmsg -e "\n--> Deploying functions ...\n"

# deploy the functions
faas-cli deploy \
  -f $fbrd/cloud_functions/openfaas/faas_benchmarker_functions.yml \
  --label "com.openfaas.scale.zero=true"

smsg -e "\nDone configuring OpenFaas\n"
