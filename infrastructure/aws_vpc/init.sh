#!/bin/bash

STATE_FILE="faas-benchmarker/aws-vpc"

echo -e "Initializing terraform with spaces backend ..."

terraform init \
    -backend-config "bucket=$SPACE_NAME" \
    -backend-config "key=$STATE_FILE" \
    -backend-config "access_key=$SPACE_KEY" \
    -backend-config "secret_key=$SPACE_SECRET_KEY"
