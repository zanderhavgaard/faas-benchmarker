#!/bin/bash

source $fbrd/fb_cli/utils.sh

function applyExperimentNameToTemplate {
  terraform_files=$(ls $experiment_context/$1/*.tf)
  for terraform_file in $terraform_files; do
    sed -i "s/changeme/$experiment_name/g" $terraform_file
  done
}

function copyTemplate {
  rm -rf "$experiment_context/$1" > /dev/null 2>&1
  cp -r "$template_path/$1" "$experiment_context/$1"
}

# where to find templates
template_path="$fbrd/infrastructure/templates"
# name of experiment, must be [a-zA-Z-]
experiment_name=$1
# where experiment files are stored
experiment_context="$fbrd/experiments/$experiment_name"

# ====================================
# Cloud functions
# ====================================

pmsg "Copying AWS Lambda template ..."
# cp -r $template_path/aws_lambda $experiment_context/aws_lambda
copyTemplate "aws_lambda"

pmsg "Applying experiment name to AWS Lambda template ..."
applyExperimentNameToTemplate "aws_lambda"

# ====================================

pmsg "Copying Azure Functions template ..."
copyTemplate "azure_functions"

pmsg "Applying experiment name to Azure Functions Template ..."
applyExperimentNameToTemplate "azure_functions"

pmsg "Copying Azure functions app source code ..."

mkdir -pv $experiment_context/azure_functions/function_code
cp -r $fbrd/cloud_functions/azure_functions/* $experiment_context/azure_functions/function_code

pmsg "Applying experiment name to copied function source code ..."

function_code_dirs=$(ls $experiment_context/azure_functions/function_code/)
for fcd in $function_code_dirs; do
    # get the function number
    fx_num=${fcd:8:1}
    exp_filename=$experiment_name$fx_num
    # rename file and directory names to experiment name
    mv $experiment_context/azure_functions/function_code/$fcd/$fcd \
      $experiment_context/azure_functions/function_code/$fcd/$exp_filename
    mv $experiment_context/azure_functions/function_code/$fcd \
      $experiment_context/azure_functions/function_code/$exp_filename
done

# ====================================
# OpenFaas is both client and cloud functions in one

pmsg "Copying OpenFaas template ..."
copyTemplate "openfaas_client_vm"

pmsg "Applying experiment name to OpenFaas template ..."
applyExperimentNameToTemplate "openfaas_client_vm"

# ====================================
# Client vms
# ====================================
# ec2 is client for azure functions

pmsg "Copying AWS ec2 client template ..."
copyTemplate "aws_ec2"

pmsg "Applying experiment name to AWS ec2 instance template ..."
applyExperimentNameToTemplate "aws_ec2"

# ====================================
# azure linuxvm is client for aws lambda

pmsg "Copying Azure linux vm client template ..."
copyTemplate "azure_linuxvm"

pmsg "Applying experiment name to Azure linux vm template ..."
applyExperimentNameToTemplate "azure_linuxvm"

# ====================================
