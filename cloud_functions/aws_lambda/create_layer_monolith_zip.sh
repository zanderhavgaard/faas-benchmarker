#!/bin/bash

cd $fbrd/cloud_functions/aws_lambda
mkdir python
pip install -r requirements_monolith.txt -t python
zip -r lambda_layer_monolith.zip python
rm -rf python
