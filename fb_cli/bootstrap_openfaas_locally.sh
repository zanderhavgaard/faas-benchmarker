#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

minikube_driver="kvm2"

pmsg "Removing any existing minikube ..."

minikube delete

pmsg "Starting minikube using $minikube_driver driver ..."

minikube start --driver=$minikube_driver
sleep 5

pmsg "Installing OpenFaas using arkade ..."

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
        --set "faasIdler.dryRun=false" \
        --set "faasIdler.inactivityDuration=10m" \
        --set "faasIdler.reconcileInterval=5m" \
        && deployed="true" \
        && smsg "Successfully deployed openfaas $fcd"
done
sleep 5

pmsg "Configuring gateway ..."

kubectl rollout status -n openfaas deploy/gateway
sleep 5

pmsg "Starting port forward ..."

kubectl port-forward -n openfaas svc/gateway 8080:8080 &
sleep 5

pmsg "Configuring faas-cli ..."

PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n "$PASSWORD" | faas-cli login --username admin --password-stdin

pmsg "Deploying functions ..."

faas-cli template pull
faas-cli deploy \
  -f $fbrd/cloud_functions/openfaas/faas_benchmarker_functions.yml \
  --label "com.openfaas.scale.zero=true"

smsg "Done configuring OpenFaas"
