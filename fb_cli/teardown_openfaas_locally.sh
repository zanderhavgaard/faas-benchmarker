#!/bin/bash

set -e

source "$fbrd/fb_cli/utils.sh"

pmsg "Destroying local minikube cluster ..."

minikube delete

pmsg "Stopping any lingering kubectl processes ..."

killall -q kubectl

pmsg "Done destroying minikube cluster ..."
