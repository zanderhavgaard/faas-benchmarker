#!/bin/bash

# exit if anything goes wrong
# TODO enable when bug is fixed when destoying azure_functions
# set -e

# parse argments
command=$1
cf_provider=$2
client_provider=$3
experiment_name=$4
experiment_context="$fbrd/experiments/$5"
env_file="$experiment_context/$experiment_name.env"
remote_env_file="/home/ubuntu/thesis-code/experiments/$5/$4.env"

echo "=================================================================================================="
echo "Infastructure Orchestrator"
echo "=================================================================================================="
echo "Command: $command"
echo "Cloud function provider: $cf_provider"
echo "Client provider: $client_provider"
echo "Experiment name: $experiment_name"
echo "Experiment context: $experiment_context"
echo "Environment file: $env_file"
echo "Remote Environment file: $remote_env_file"
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

            echo -e "\n--> Copying AWS Lambda functions template ...\n"

            cp -r $template_path/aws_lambda $experiment_context
            cd $experiment_context/aws_lambda

            echo -e "\n--> Applying experiment name to copied template ...\n"
            terraform_files=$(ls *.tf)
            for terraform_file in $terraform_files; do
                sed "s/changeme/$experiment_name/g" $terraform_file > $experiment_name\_$terraform_file
                rm $terraform_file
            done

            echo -e "\n--> Initializing terraform ...\n"
            terraform init

            echo -e "\n--> Creating functions ...\n"
            terraform apply -auto-approve

            echo -e "\n--> Outputting variables to experiment.env ...\n"
            terraform output >> "../$experiment_name.env"

            cd $experiment_context

            echo -e "\n--> Done creating cloud functions!\n"

            ;;

        azure_functions)


            echo -e "\n--> Copying Azure functions template ...\n"

            cp -r $template_path/azure_functions $experiment_context
            cd $experiment_context/azure_functions

            echo -e "\n--> Applying experiment name to copied template ...\n"
            terraform_files=$(ls *.tf)
            for terraform_file in $terraform_files; do
                sed "s/changeme/$experiment_name/g" $terraform_file > $experiment_name\_$terraform_file
                rm $terraform_file
            done

            echo -e "\n--> Copying Azure functions app source code ...\n"

            mkdir $experiment_context/azure_functions/function_code
            cp -r $fbrd/cloud_functions/azure_functions/* $experiment_context/azure_functions/function_code

            echo -e "\n--> Applying experiment name to copied  function source code ...\n"

            function_code_dirs=$(ls function_code/)
            for fcd in $function_code_dirs; do
                # get the function number
                fx_num=${fcd:8:1}
                exp_filename=$experiment_name$fx_num
                # file and directory names
                mv function_code/$fcd/$fcd function_code/$fcd/$exp_filename
                mv function_code/$fcd function_code/$exp_filename
            done

            echo -e "\n--> Initializing terraform ...\n"
            terraform init

            echo -e "\n--> Creating functions ...\n"
            terraform apply -auto-approve

            echo -e "\n--> Outputting variables to experiment.env ...\n"
            terraform output >> "../$experiment_name.env"

            cd $experiment_context

            echo -e "\n--> Done creating cloud functions!\n"


            ;;

        openfaas)
            echo 'openfaas'
            echo "not implemented yet"
            ;;
        *)
            echo "Please specify a valid cloud function provider."
            echo "Options are: aws_lambda azure_functions openfaas"
    esac

    echo "================================="
    echo "= Done creating cloud functions ="
    echo "================================="

    case $client_provider in
        aws_ec2)

            echo -e "\n--> Copying AWS ec2 template ...\n"

            cp -r $template_path/aws_ec2 $experiment_context
            cd $experiment_context/aws_ec2

            echo -e "\n--> Applying experiment name to copied template ...\n"
            terraform_files=$(ls *.tf)
            for terraform_file in $terraform_files; do
                sed "s/changeme/$experiment_name/g" $terraform_file > $experiment_name\_$terraform_file
                rm $terraform_file
            done

            echo -e "\n--> Initializing terraform ...\n"
            terraform init

            echo -e "\n--> Creating client infrastructure ...\n"
            terraform apply \
                -auto-approve \
                -var "env_file=$env_file" \
                -var "remote_env_file=$remote_env_file" \

            echo -e "\n--> Outputting variables to client.env ...\n"
            terraform output >> "../client.env"

            cd $experiment_context

            echo -e "\n--> Done creating client infrastructure!\n"

            ;;

        azure_linuxvm)

            echo -e "\n--> Copying Azure linux vm template ...\n"

            cp -r $template_path/azure_linuxvm $experiment_context
            cd $experiment_context/azure_linuxvm

            echo -e "\n--> Applying experiment name to copied template ...\n"
            terraform_files=$(ls *.tf)
            for terraform_file in $terraform_files; do
                sed "s/changeme/$experiment_name/g" $terraform_file > $experiment_name\_$terraform_file
                rm $terraform_file
            done

            echo -e "\n--> Initializing terraform ...\n"
            terraform init

            echo -e "\n--> Creating client infrastructure ...\n"
            terraform apply \
                -auto-approve \
                -var "env_file=$env_file" \
                -var "remote_env_file=$remote_env_file" \

            echo -e "\n--> Outputting variables to client.env ...\n"
            terraform output >> "../client.env"

            cd $experiment_context

            echo -e "\n--> Done creating client infrastructure!\n"

            ;;

        *)
            echo "Please specify a valid provider for client."
            echo "Valid options are: aws_ec2 azure_linuxvm"
    esac


    echo "================================="
    echo "= Done creating cloud client vm ="
    echo "================================="

#  ____  _____ ____ _____ ____   _____   __
# |  _ \| ____/ ___|_   _|  _ \ / _ \ \ / /
# | | | |  _| \___ \ | | | |_) | | | \ V /
# | |_| | |___ ___) || | |  _ <| |_| || |
# |____/|_____|____/ |_| |_| \_\\___/ |_|

elif [ $command == "destroy" ]; then

    case $cf_provider in
        aws_lambda)

            echo -e "\n--> Destroying experiment cloud function infrastructure ...\n"

            cd $experiment_context/aws_lambda
            terraform destroy -auto-approve
            cd $experiment_context

            echo -e "\n--> Removing experiment infrastructure files ...\n"
            rm -rf $experiment_context/aws_lambda

            echo -e "\n--> Done destroying! \n"

            ;;
        azure_functions)

            echo -e "\n--> Destroying experiment cloud function infrastructure ...\n"

            cd $experiment_context/azure_functions
            terraform destroy -auto-approve
            # TODO fix, seems to be some bug when destroying function resources, though everything is deleted if run again??
            terraform destroy -auto-approve
            terraform destroy -auto-approve
            terraform destroy -auto-approve
            cd $experiment_context

            echo -e "\n--> Removing experiment infrastructure files ...\n"
            rm -rf $experiment_context/azure_functions

            echo -e "\n--> Done destroying! \n"

            ;;
        openfaas)
            echo 'openfaas'
            echo "not implemented yet"
            ;;
        *)
            echo "Please specify a valid cloud function provider."
            echo "Options are: aws_lambda azure_functions openfaas"
    esac

    echo "==================================="
    echo "= Done destroying cloud functions ="
    echo "==================================="

    case $client_provider in
        aws_ec2)

            echo -e "\n--> Destroying experiment client infrastructure ...\n"

            cd $experiment_context/aws_ec2
            terraform destroy \
                -auto-approve \
                -var "env_file=$env_file" \
                -var "remote_env_file=$remote_env_file"

            cd $experiment_context

            echo -e "\n--> Removing experiment infrastructure files ...\n"
            rm -rf $experiment_context/aws_ec2

            echo -e "\n--> Done destroying! \n"

            ;;
        azure_linuxvm)

            echo -e "\n--> Destroying experiment client infrastructure ...\n"

            cd $experiment_context/azure_linuxvm
            terraform destroy \
                -auto-approve \
                -var "env_file=$env_file" \
                -var "remote_env_file=$remote_env_file"

            cd $experiment_context

            echo -e "\n--> Removing experiment infrastructure files ...\n"
            rm -rf $experiment_context/azure_linuxvm

            echo -e "\n--> Done destroying! \n"
            ;;

        *)
            echo "Please specify a valid provider for client."
            echo "Valid options are: aws_ec2 azure_linuxvm"
    esac

            echo -e "\n--> Removing experiment.env ...\n"
            rm $experiment_context/$experiment_name.env

            echo -e "\n--> Removing client.env file ...\n"
            rm $experiment_context/client.env

    echo "==================================="
    echo "= Done destroying cloud client vm ="
    echo "==================================="
fi
