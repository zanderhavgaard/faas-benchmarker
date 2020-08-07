#!/bin/bash

faas-cli template pull
faas-cli template store pull python3-flask

config_yaml="faas_benchmarker_functions.yml"

faas-cli build -f $config_yaml

faas-cli push -f $config_yaml

[[ "$*" = *--deploy* ]] && faas-cli deploy -f $config_yaml
