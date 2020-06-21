#!/bin/bash

source "fb_cli/utils.sh"

repo_name="faasbenchmarker"
client_image="$repo_name/client"
webui_image="$repo_name/webui"
db_image="$repo_name/exp_mysql"

git_sha=$(git rev-parse --short HEAD)

pmsg "Building new client docker image ..."
docker build -f "Dockerfile" -t "$client_image:$git_sha" .
docker tag "$client_image:$git_sha" "$client_image:latest"

pmsg "Building new webui image ..."
docker build -f "webserver/Dockerfile" -t "$webui_image:$git_sha" "./webserver"
docker tag "$webui_image:$git_sha" "$webui_image:latest"

pmsg "Building new database image ..."
docker build -f "benchmark/docker_mysql/Dockerfile" -t "$db_image:$git_sha" "./benchmark/docker_mysql"
docker tag "$db_image:$git_sha" "$db_image:latest"

smsg "Done buidling new images."
