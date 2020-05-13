#!/bin/bash
docker build -t faasbenchmarker/s3cmd:latest -f Dockerfile-s3cmd .
# docker push faasbenchmarker/s3cmd:latest
