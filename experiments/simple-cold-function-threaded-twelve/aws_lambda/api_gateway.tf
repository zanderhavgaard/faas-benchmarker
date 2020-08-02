# create IAM role for lambdas
resource "aws_iam_role" "simple-cold-function-threaded-twelve-role" {
  name = "simple-cold-function-threaded-twelve-role"
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
  role = aws_iam_role.simple-cold-function-threaded-twelve-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "simple-cold-function-threaded-twelve-api" {
  name = "simple-cold-function-threaded-twelve"
  description = "simple-cold-function-threaded-twelve/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "simple-cold-function-threaded-twelve-prod" {
  depends_on = [
    aws_api_gateway_integration.simple-cold-function-threaded-twelve1-api-integration,
    aws_api_gateway_integration.simple-cold-function-threaded-twelve2-api-integration,
    aws_api_gateway_integration.simple-cold-function-threaded-twelve3-api-integration,
    aws_api_gateway_integration.monolith-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.simple-cold-function-threaded-twelve-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "simple-cold-function-threaded-twelve-key" {
  name = "simple-cold-function-threaded-twelve-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "simple-cold-function-threaded-twelve" {
  name         = "simple-cold-function-threaded-twelve-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.simple-cold-function-threaded-twelve-api.id
    stage  = aws_api_gateway_deployment.simple-cold-function-threaded-twelve-prod.stage_name
  }

  throttle_settings {
    burst_limit = 1000
    rate_limit  = 1000
  }
}

# attach api key to useage plan
resource "aws_api_gateway_usage_plan_key" "simple-cold-function-threaded-twelve" {
  key_id        = aws_api_gateway_api_key.simple-cold-function-threaded-twelve-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.simple-cold-function-threaded-twelve.id
}
