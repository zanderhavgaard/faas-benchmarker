#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

pmsg "This will create ALL infrastructure for ALL experiments, would you like to continue? [yes/no]"
read -n 3 -r ; echo
if [[ $REPLY =~ ^yes$ ]]; then

    experiments=$(ls -I "*.md" "$fbrd/experiments")

    for exp in $experiments ; do
        pmsg "Now bootstrapping experiment: $exp"
        bash "$fbrd/dev_tools/bootstrap_infrastructure_experiment.sh" "$exp" --skip-prompt
    done
else
    errmsg "Aborting ..."
fi
