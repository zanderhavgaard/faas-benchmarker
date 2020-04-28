#!/bin/bash

# check that environment variables are set
env_vars="
fbrd
SPACE_NAME
SPACE_KEY
SPACE_SECRET_KEY
TF_VAR_do_token
TF_VAR_do_region
TF_VAR_aws_access_key
TF_VAR_aws_secret_key
TF_VAR_aws_datacenter_region
TF_VAR_subscription_id
TF_VAR_client_id
TF_VAR_client_secret
TF_VAR_tenant_id
TF_VAR_azure_region
TF_VAR_db_pvt_key
TF_VAR_db_pub_key
TF_VAR_db_ssh_fingerprint
TF_VAR_client_pvt_key
TF_VAR_client_pub_key
TF_VAR_client_ssh_fingerprint
TF_VAR_orch_pvt_key
TF_VAR_orch_pub_key
TF_VAR_orch_ssh_fingerprint
"
for env_var in $env_vars ; do
  [ -z "${!env_var}" ] && echo "Environment variable $env_var is not set." && exit
done
