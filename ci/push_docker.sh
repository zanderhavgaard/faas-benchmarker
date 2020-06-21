#!/bin/bash

source "fb_cli/utils.sh"

repo_name="faasbenchmarker"
client_image="$repo_name/client"
webui_image="$repo_name/webui"
db_image="$repo_name/exp_mysql"

git_sha=$(git rev-parse --short HEAD)

pmsg "Pusing client image ..."
docker push "$client_image:$git_sha"
docker push "$client_image:latest"

pmsg "Pusing webui image ..."
docker push "$webui_image:$git_sha"
docker push "$webui_image:latest"

pmsg "Pusing db image ..."
docker push "$db_image:$git_sha"
docker push "$db_image:latest"

smsg "Done pushing new image."
