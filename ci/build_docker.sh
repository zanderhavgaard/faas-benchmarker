#!/bin/bash

source "fb_cli/utils.sh"

IMAGE_NAME='faasbenchmarker/client'
GIT_SHA=$(git rev-parse --short HEAD)
TAG="$IMAGE_NAME:$GIT_SHA"

pmsg "Building new docker images ..."
docker build -f "Dockerfile" -t "$TAG" .

pmsg "Tagging new docker image with latest"
docker tag "$TAG" "$IMAGE_NAME:latest"

smsg "Done buidling new image."
