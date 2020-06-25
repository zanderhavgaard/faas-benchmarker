#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

pmsg "Removing existing .yml files ..."
rm $fbrd/dev_tools/dragon_server/openfaas_deploy_yaml/*

pmsg "Generating openfaas function deployment yaml files ..."

experiments=$(ls -I "*.md" "$fbrd/experiments")

for exp in $experiments ; do
    pmsg "Generating yaml deployment file for experiment: $exp"
   sed "s/changeme/$exp/g" "$fbrd/dev_tools/dragon_server/faas_benchmarker_functions.yml" > "$fbrd/dev_tools/dragon_server/openfaas_deploy_yaml/$exp.yml"
done

smsg "Done generating yaml files."
