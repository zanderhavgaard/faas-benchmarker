#!/bin/bash

# exit if anything goes wrong
set -e

# parse argments
command=$1
cf_provider=$2
client_provider=$3
experiment_name=$4
experiment_context="$fbrd/experiments/$5"

echo "=================================================================================================="
echo "Infastructure Orchestrator"
echo "=================================================================================================="
echo "Command: $command"
echo "Cloud function provider: $cf_provider"
echo "Client provider: $client_provider"
echo "Experiment name: $experiment_name"
echo "Experiment context: $experiment_context"
echo "=================================================================================================="

# vars
template_path="$fbrd/infrastructure/templates"

#   ____ ____  _____    _  _____ _____
#  / ___|  _ \| ____|  / \|_   _| ____|
# | |   | |_) |  _|   / _ \ | | |  _|
# | |___|  _ <| |___ / ___ \| | | |___
#  \____|_| \_\_____/_/   \_\_| |_____|


if [ $command == "create" ]; then

    # generate cloud functions
    case $cf_provider in
        aws_lambda)

            echo -e "\nCopying AWS Lambda functions template ...\n"

            cp -r $template_path/aws_lambda_template $experiment_context
            cd $experiment_context/aws_lambda_template

            if [ ! -d $experiment_context/aws_lambda_template/.terraform ]; then
                echo -e "\nInitializing terraform ...\n"
                terraform init
            fi

            echo -e "\nCreating functions ...\n"
            terraform apply -auto-approve

            echo -e "\nOutputting variables to experiment.env ...\n"
            terraform output >> ../experiment.env

            echo -e "\nDone creating cloud functions!\n"

            ;;
        azure_functions)
            echo 'azure'
            echo "not implemented yet"
            ;;
        openfaas)
            echo 'openfaas'
            echo "not implemented yet"
            ;;
        *)
            echo "Please specify a valid cloud function provider."
            echo "Options are: aws_lambda azure_functions openfaas"
    esac

    case $client_provider in
        aws)
            echo aws
            echo "not implemented yet"
            ;;
        azure)
            echo azure
            echo "not implemented yet"
            ;;
        *)
            echo "Please specify a valid provider for client."
            echo "Valid options are: aws_ec2 azure_linux_vm"
    esac

#  ____  _____ ____ _____ ____   _____   __
# |  _ \| ____/ ___|_   _|  _ \ / _ \ \ / /
# | | | |  _| \___ \ | | | |_) | | | \ V /
# | |_| | |___ ___) || | |  _ <| |_| || |
# |____/|_____|____/ |_| |_| \_\\___/ |_|

elif [ $command == "destroy" ]; then

    case $cf_provider in
        aws_lambda)

            echo -e "\nDestroying experiment cloud function infrastructure ...\n"

            cd $experiment_context/aws_lambda_template
            terraform destroy -auto-approve
            cd $experiment_context

            echo -e "\nRemoving experiment infrastructure files ...\n"
            rm -rf $experiment_context/aws_lambda_template

            echo -e "\nRemoving experiment.env ...\n"
            rm $experiment_context/experiment.env

            echo -e "\nDone destroying! \n"

            ;;
        azure_functions)
            echo 'azure'
            echo "not implemented yet"
            ;;
        openfaas)
            echo 'openfaas'
            echo "not implemented yet"
            ;;
        *)
            echo "Please specify a valid cloud function provider."
            echo "Options are: aws_lambda azure_functions openfaas"
    esac

    case $client_provider in
        aws_ec2)
            echo aws
            echo "not implemented yet"
            ;;
        azure_linux_vm)
            echo azure
            echo "not implemented yet"
            ;;
        *)
    esac

fi
