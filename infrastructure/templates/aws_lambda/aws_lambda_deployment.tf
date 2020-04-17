# create a aws lambda cloud function environment
# setup with an API gateway and a lambda function using the
# python 3.7 runtime
# based on: https://learn.hashicorp.com/terraform/aws/lambda-api-gateway

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_token" {}
variable "aws_datacenter_region" {}

# path to lambda function code
variable "path_to_code" {
  type = string
  default = "../../../cloud_functions/aws_lambda"
}

# loacal variables
locals {
  aws_region = "eu-central-1"
}

# setup aws provider
provider "aws" {
  region = var.aws_datacenter_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  token = var.aws_token
  version = "2.51"
}

provider "archive" {
  veriosn = "1.3"
}

# create IAM role for lambdas
resource "aws_iam_role" "changeme-role" {
  name = "changeme-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# attach permission to the iam role to allow lambdas to invoke other lambdas
resource "aws_iam_role_policy_attachment" "lambda-full-access" {
  role = aws_iam_role.changeme-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "changeme-api" {
  name = "changeme"
  description = "changeme/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "changeme-prod" {
  depends_on = [
    aws_api_gateway_integration.changeme1-api-integration,
    aws_api_gateway_integration.changeme2-api-integration,
    aws_api_gateway_integration.changeme3-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.changeme-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "changeme-key" {
  name = "changeme-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "changeme" {
  name         = "changeme-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.changeme-api.id
    stage  = aws_api_gateway_deployment.changeme-prod.stage_name
  }

  quota_settings {
    limit  = 2000
    offset = 0
    period = "DAY"
  }

  throttle_settings {
    burst_limit = 1000
    rate_limit  = 1000
  }
}

# attach api key to useage plan
resource "aws_api_gateway_usage_plan_key" "changeme" {
  key_id        = aws_api_gateway_api_key.changeme-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.changeme.id
}

# output the invocation url
output "invoke_url" {
  value = aws_api_gateway_deployment.changeme-prod.invoke_url
}

# output the api key
output "api_key" {
  value = aws_api_gateway_api_key.changeme-key.value
}
