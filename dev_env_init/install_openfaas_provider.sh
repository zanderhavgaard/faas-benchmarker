#!/bin/bash

# install the openfaas terraform provider plugin

version="v0.3.1"

wget https://github.com/ewilde/terraform-provider-openfaas/releases/download/v0.3.1/terraform-provider-openfaas_0.3.1_linux_amd64.zip
unzip terraform-provider-openfaas_0.3.1_linux_amd64.zip
rm terraform-provider-openfaas_0.3.1_linux_amd64.zip
mkdir -pv ~/.terraform.d/plugins/linux_amd64
mv terraform-provider-openfaas_v0.3.1 ~/.terraform.d/plugins/linux_amd64
