#!/bin/bash

source $fbrd/fb_cli/utils.sh

function applyExperimentNameToTemplate {
  terraform_files=$(ls $experiment_context/$1/*.tf)
  for terraform_file in $terraform_files; do
    sed -i "s/changeme/$experiment_name/g" "$terraform_file"
  done
}

# where to find templates
template_path="$fbrd/infrastructure/templates"
# name of experiment, must be [a-zA-Z-]
experiment_name=$1
# where experiment files are stored
experiment_context="$fbrd/experiments/$experiment_name"

pmsg "Creating new experiment: $experiment_name from templates..."

pmsg "Will store new experiment in $experiment_context"

pmsg "Creating experiment directory ..."

mkdir -pv "$experiment_context"

pmsg "Creating python experiment file from template ..."
cp "$fbrd/experiment_template/template.py" "$experiment_context/$experiment_name.py"

pmsg "Copying infrastructure template files ..."
bash "$fbrd/fb_cli/copy_infrastructure_templates_to_experiment.sh" "$experiment_name"

# TODO add orchestration

pmsg "\n\tDone creating experiment from templates, experiment files ar located in faas-benchmarker/experiments/$experiment_name\n"
