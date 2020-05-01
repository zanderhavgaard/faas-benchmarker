#!/bin/bash

function msg {
  green="\033[01;32m"
  bold="\033[1m"
  none="\033[00m"
  echo -e "${green}-->${none} ${bold}$1${none}"
}

function applyExperimentNameToTemplate {
  terraform_files=$(ls $experiment_context/$1/*.tf)
  for terraform_file in $terraform_files; do
    sed -i "s/changeme/$experiment_name/g" $terraform_file
  done
}

function copyTemplate {
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

msg "Copying AWS Lambda template ..."
# cp -r $template_path/aws_lambda $experiment_context/aws_lambda
copyTemplate "aws_lambda"

msg "Applying experiment name to AWS Lambda template ..."
applyExperimentNameToTemplate "aws_lambda"

# ====================================

msg "Copying Azure Functions template ..."
copyTemplate "azure_functions"

msg "Applying experiment name to Azure Functions Template ..."
applyExperimentNameToTemplate "azure_functions"

msg "Copying Azure functions app source code ..."

mkdir -pv $experiment_context/azure_functions/function_code
cp -r $fbrd/cloud_functions/azure_functions/* $experiment_context/azure_functions/function_code

msg "Applying experiment name to copied function source code ..."

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

msg "Copying OpenFaas template ..."
copyTemplate "openfaas_client_vm"

msg "Applying experiment name to OpenFaas template ..."
applyExperimentNameToTemplate "openfaas_client_vm"

# ====================================
# Client vms
# ====================================
# ec2 is client for azure functions

msg "Copying AWS ec2 client template ..."
copyTemplate "aws_ec2"

msg "Applying experiment name to AWS ec2 instance template ..."
applyExperimentNameToTemplate "aws_ec2"

# ====================================
# azure linuxvm is client for aws lambda

msg "Copying Azure linux vm client template ..."
copyTemplate "azure_linuxvm"

msg "Applying experiment name to Azure linux vm template ..."
applyExperimentNameToTemplate "azure_linuxvm"

# ====================================
