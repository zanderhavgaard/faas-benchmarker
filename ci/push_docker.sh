#!/bin/bash

source "fb_cli/utils.sh"

IMAGE_NAME='faasbenchmarker/client'
GIT_SHA=$(git rev-parse --short HEAD)
TAG="$IMAGE_NAME:$GIT_SHA"

pmsg "Pushing new image with git sha tag ..."
docker push "$TAG"

pmsg "Pushing new image with latest tag ..."
docker push "$IMAGE_NAME:latest"

smsg "Done pushing new image."
