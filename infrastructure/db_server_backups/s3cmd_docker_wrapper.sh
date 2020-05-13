#!/bin/bash

command=$1

access_key=$SPACE_KEY
secret_access_key=$SPACE_SECRET_KEY
space_name=$SPACE_NAME

if [ $command = "ls" ]; then
    docker run \
        --rm \
        -it \
        -e AWS_ACCESS_KEY_ID="$access_key" \
        -e AWS_SECRET_ACCESS_KEY="$secret_access_key" \
        faasbenchmarker/s3cmd \
        s3cmd ls --recursive "s3://$SPACE_NAME"
elif [ $command = "it" ]; then
    docker run \
        --rm \
        -it \
        -e AWS_ACCESS_KEY_ID="$access_key" \
        -e AWS_SECRET_ACCESS_KEY="$secret_access_key" \
        --mount type=bind,source="$(pwd)",target=/home/arch/shared \
        faasbenchmarker/s3cmd
else
    echo "Please use a valid command: ls, it"
fi
