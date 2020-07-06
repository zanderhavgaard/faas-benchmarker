#!/bin/bash

functions=$(ls openfaas_deploy_yaml )

for yaml in $functions ; do
   faas-cli remove -f "openfaas_deploy_yaml/$yaml" \
      --label "com.openfaas.scale.zero=true"
done
