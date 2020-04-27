#!/bin/bash

STATE_FILE="faas-benchmarker/orchestrator"

echo -e "\nInitializing terraform with spaces backend ...\n"

terraform init \
    -backend-config "bucket=$SPACE_NAME" \
    -backend-config "key=$STATE_FILE" \
    -backend-config "access_key=$SPACE_KEY" \
    -backend-config "secret_key=$SPACE_SECRET_KEY"
