#!/bin/bash

# This script is used to install all of the depencies for
# orchestrating the openfaas on eks/fargate bootstap

# install aws cli
curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
unzip awscli-bundle.zip
sudo python3 awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
rm -rf awscli-bundle
rm awscli-bundle.zip

# install eksctl
# https://github.com/weaveworks/eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# install kubectl
# https://kubernetes.io/docs/tasks/tools/install-kubectl/
curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

# install helm
# https://helm.sh/docs/intro/install/
curl "https://get.helm.sh/helm-v3.2.3-linux-amd64.tar.gz" -o "helm.tar.gz"
tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
rm -rf linux-amd64
rm helm.tar.gz

# install arkade
# https://github.com/alexellis/arkade
curl -SLfs https://dl.get-arkade.dev | sudo sh

# install faas-cli
# https://github.com/openfaas/faas-cli/
curl -SLfs https://cli.openfaas.com | sudo sh
