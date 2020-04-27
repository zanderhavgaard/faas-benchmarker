#!/bin/bash

set -e

echo -e "\n--> Destroying local minikube cluster ...\n"

minikube delete

echo -e "\n--> Stopping any lingering kubectl processes ...\n"

killall -q kubectl

echo -e "\n--> Done destroying minikube cluster ...\n"
