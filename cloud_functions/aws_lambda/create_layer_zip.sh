#!/bin/bash

cd $fbrd/cloud_functions/aws_lambda
mkdir python
pip install -r requirements.txt -t python
zip -r lambda_layer.zip python
rm -rf python
