#!/bin/bash

config_yaml="faas_benchmarker_functions.yml"

faas-cli build -f $config_yaml

faas-cli push -f $config_yaml

faas-cli deploy -f $config_yaml
