# create IAM role for lambdas
resource "aws_iam_role" "coldstart-identifier-nested-role" {
  name = "coldstart-identifier-nested-role"
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
  role = aws_iam_role.coldstart-identifier-nested-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "coldstart-identifier-nested-api" {
  name = "coldstart-identifier-nested"
  description = "coldstart-identifier-nested/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "coldstart-identifier-nested-prod" {
  depends_on = [
    aws_api_gateway_integration.coldstart-identifier-nested1-api-integration,
    aws_api_gateway_integration.coldstart-identifier-nested2-api-integration,
    aws_api_gateway_integration.coldstart-identifier-nested3-api-integration,
    aws_api_gateway_integration.monolith-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.coldstart-identifier-nested-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "coldstart-identifier-nested-key" {
  name = "coldstart-identifier-nested-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "coldstart-identifier-nested" {
  name         = "coldstart-identifier-nested-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.coldstart-identifier-nested-api.id
    stage  = aws_api_gateway_deployment.coldstart-identifier-nested-prod.stage_name
  }

  throttle_settings {
    burst_limit = 1000
    rate_limit  = 1000
  }
}

# attach api key to useage plan
resource "aws_api_gateway_usage_plan_key" "coldstart-identifier-nested" {
  key_id        = aws_api_gateway_api_key.coldstart-identifier-nested-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.coldstart-identifier-nested.id
}
