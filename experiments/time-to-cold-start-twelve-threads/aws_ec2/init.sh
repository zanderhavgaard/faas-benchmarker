#!/bin/bash

experiment_name=$1

STATE_FILE="faas-benchmarker/aws-ec2/$experiment_name"

echo -e "Initializing terraform with spaces backend ..."

terraform init \
    -backend-config "bucket=$SPACE_NAME" \
    -backend-config "key=$STATE_FILE" \
    -backend-config "access_key=$SPACE_KEY" \
    -backend-config "secret_key=$SPACE_SECRET_KEY"
