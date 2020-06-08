# create IAM role for lambdas
resource "aws_iam_role" "single-function-time-to-cold-start-role" {
  name = "single-function-time-to-cold-start-role"
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
  role = aws_iam_role.single-function-time-to-cold-start-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "single-function-time-to-cold-start-api" {
  name = "single-function-time-to-cold-start"
  description = "single-function-time-to-cold-start/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "single-function-time-to-cold-start-prod" {
  depends_on = [
    aws_api_gateway_integration.single-function-time-to-cold-start1-api-integration,
    aws_api_gateway_integration.single-function-time-to-cold-start2-api-integration,
    aws_api_gateway_integration.single-function-time-to-cold-start3-api-integration,
    aws_api_gateway_integration.monolith-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.single-function-time-to-cold-start-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "single-function-time-to-cold-start-key" {
  name = "single-function-time-to-cold-start-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "single-function-time-to-cold-start" {
  name         = "single-function-time-to-cold-start-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.single-function-time-to-cold-start-api.id
    stage  = aws_api_gateway_deployment.single-function-time-to-cold-start-prod.stage_name
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
resource "aws_api_gateway_usage_plan_key" "single-function-time-to-cold-start" {
  key_id        = aws_api_gateway_api_key.single-function-time-to-cold-start-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.single-function-time-to-cold-start.id
}
