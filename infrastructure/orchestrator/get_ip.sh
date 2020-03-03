#!/bin/bash

# regex ip address
[[ $(grep ipv4_address terraform.tfstate) =~ ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+) ]]
ip=${BASH_REMATCH[1]}

echo -e "Orchestrator server is running at: $ip"
echo -e "ssh root@$ip -i <key-path>"
