#!/bin/bash

docker build -f Dockerfile_azure_functions -t faasbenchmarker/azfunc:latest .
docker push faasbenchmarker/azfunc:latest
