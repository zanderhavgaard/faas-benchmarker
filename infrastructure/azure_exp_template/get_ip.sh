#!/bin/bash

# regex ip address
[[ $(grep public_ip terraform.tfstate) =~ ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+) ]]
ip=${BASH_REMATCH[1]}

echo -e "Azure linux server is running at: $ip"
echo -e "ssh ubuntu@$ip -i <key-path>"
