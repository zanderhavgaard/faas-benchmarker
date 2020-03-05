# this terraform file creates a simple 'hello world' aws lambda
# setup with an API gateway and a lambda function using the
# python 3.7 runtime
# based on: https://learn.hashicorp.com/terraform/aws/lambda-api-gateway

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_account_id" {}

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

# creates zip archive containing lambda code
data "archive_file" "hw-lambda-code" {
  type = "zip"
  source_file = "lambda_function.py"
  output_path = "lambda.zip"
}

# creates zip archive containing lambda code
data "archive_file" "hw2-lambda-code" {
  type = "zip"
  source_file = "lambda_function2.py"
  output_path = "lambda2.zip"
}

# create lambda function
resource "aws_lambda_function" "hw-python" {
  filename = data.archive_file.hw-lambda-code.output_path
  function_name = "hw-python"
  role = aws_iam_role.hw-role.arn
  handler = "lambda_function.lambda_handler"
  runtime = "python3.7"
  source_code_hash = filemd5(data.archive_file.hw-lambda-code.output_path)
  publish = true
}

resource "aws_lambda_function" "hw2-python" {
  filename = data.archive_file.hw2-lambda-code.output_path
  function_name = "hw2-python"
  role = aws_iam_role.hw-role.arn
  handler = "lambda_function2.lambda_handler"
  runtime = "python3.7"
  source_code_hash = filemd5(data.archive_file.hw2-lambda-code.output_path)
  publish = true
}

# create IAM role for lambdas
resource "aws_iam_role" "hw-role" {
  name = "hw-role"
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

# create API gateway
resource "aws_api_gateway_rest_api" "hw-api" {
  name = "hello-world-python"
  description = "Hello world python terraform template"
}

# create API endpoint
resource "aws_api_gateway_resource" "hw-api-resource" {
  rest_api_id = aws_api_gateway_rest_api.hw-api.id
  parent_id = aws_api_gateway_rest_api.hw-api.root_resource_id
  path_part = "hello"
}

# create API endpoint method
resource "aws_api_gateway_method" "hw-lambda-method" {
  rest_api_id = aws_api_gateway_rest_api.hw-api.id
  resource_id = aws_api_gateway_resource.hw-api-resource.id
  http_method = "GET"
  authorization = "None" # TODO add auth
  api_key_required = true
}

# point API endpoint at lambda function
resource "aws_api_gateway_integration" "hw-api-integration" {
  rest_api_id = aws_api_gateway_rest_api.hw-api.id
  resource_id = aws_api_gateway_method.hw-lambda-method.resource_id
  http_method = aws_api_gateway_method.hw-lambda-method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.hw-python.invoke_arn
}

# add permission for gateway to invoke lambdas
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hw-python.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.hw-api.execution_arn}/*/*"
}

# create API endpoint
resource "aws_api_gateway_resource" "hw2-api-resource" {
  rest_api_id = aws_api_gateway_rest_api.hw-api.id
  parent_id = aws_api_gateway_rest_api.hw-api.root_resource_id
  path_part = "hello2"
}

# create API endpoint method
resource "aws_api_gateway_method" "hw2-lambda-method" {
  rest_api_id = aws_api_gateway_rest_api.hw-api.id
  resource_id = aws_api_gateway_resource.hw2-api-resource.id
  http_method = "GET"
  authorization = "None" # TODO add auth
  api_key_required = true
}

# point API endpoint at lambda function
resource "aws_api_gateway_integration" "hw2-api-integration" {
  rest_api_id = aws_api_gateway_rest_api.hw-api.id
  resource_id = aws_api_gateway_method.hw2-lambda-method.resource_id
  http_method = aws_api_gateway_method.hw2-lambda-method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.hw2-python.invoke_arn
}

# add permission for gateway to invoke lambdas
resource "aws_lambda_permission" "apigw2" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hw2-python.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.hw-api.execution_arn}/*/*"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "hw-prod" {
  depends_on = [
    aws_api_gateway_integration.hw-api-integration,
    aws_api_gateway_integration.hw2-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.hw-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "hw-key" {
  name = "hw-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "hw" {
  name         = "hw-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.hw-api.id
    stage  = aws_api_gateway_deployment.hw-prod.stage_name
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
resource "aws_api_gateway_usage_plan_key" "hw" {
  key_id        = aws_api_gateway_api_key.hw-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.hw.id
}

# output the invocation url
output "invoke_url" {
  value = aws_api_gateway_deployment.hw-prod.invoke_url
}

# output the api key
output "api_key" {
  value = aws_api_gateway_api_key.hw-key.value
}
