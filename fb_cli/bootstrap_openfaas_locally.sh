#!/bin/bash

set -e

minikube_driver="kvm2"

echo -e "\n--> Removing any existing minikube ...\n"

minikube delete

echo -e "\n--> Starting minikube using $minikube_driver driver ...\n"

minikube start --driver=$minikube_driver
sleep 5

echo -e "\n--> Installing OpenFaas using arkade ...\n"

arkade install openfaas --wait
sleep 5

echo -e "\n--> Configuring gateway ...\n"

kubectl rollout status -n openfaas deploy/gateway
sleep 5

echo -e "\n--> Starting port forward ...\n"

kubectl port-forward -n openfaas svc/gateway 8080:8080 &
sleep 5

echo -e "\n--> Configuring faas-cli ...\n"

PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n "$PASSWORD" | faas-cli login --username admin --password-stdin

echo -e "\n--> Deploying functions ...\n"

faas-cli template pull
faas-cli deploy -f $fbrd/cloud_functions/openfaas/faas_benchmarker_functions.yml

echo -e "\n--> Done configuring OpenFaas\n"
