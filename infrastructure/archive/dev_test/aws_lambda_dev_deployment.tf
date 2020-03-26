# this terraform file creates a simple 'hello world' aws lambda
# setup with an API gateway and a lambda function using the
# python 3.7 runtime
# based on: https://learn.hashicorp.com/terraform/aws/lambda-api-gateway

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_account_id" {}

# path to lambda function code
variable "path_to_code" {
  type = string
  default = "../../cloud_functions/aws_lambda"
}

# loacal variables
locals {
  aws_region = "eu-central-1"
}

# setup aws provider
provider "aws" {
  region = local.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  version = "2.51"
}

# create IAM role for lambdas
resource "aws_iam_role" "dev-role" {
  name = "dev-role"
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
  role = aws_iam_role.dev-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "dev-api" {
  name = "dev"
  description = "dev/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "dev-prod" {
  depends_on = [
    aws_api_gateway_integration.dev1-api-integration,
    aws_api_gateway_integration.dev2-api-integration,
    aws_api_gateway_integration.dev3-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.dev-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "dev-key" {
  name = "dev-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "dev" {
  name         = "dev-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.dev-api.id
    stage  = aws_api_gateway_deployment.dev-prod.stage_name
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
resource "aws_api_gateway_usage_plan_key" "dev" {
  key_id        = aws_api_gateway_api_key.dev-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.dev.id
}

# output the invocation url
output "invoke_url" {
  value = aws_api_gateway_deployment.dev-prod.invoke_url
}

# output the api key
output "api_key" {
  value = aws_api_gateway_api_key.dev-key.value
}
