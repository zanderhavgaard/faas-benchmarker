# create IAM role for lambdas
resource "aws_iam_role" "dev-experiment-role" {
  name = "dev-experiment-role"
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
  role = aws_iam_role.dev-experiment-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "dev-experiment-api" {
  name = "dev-experiment"
  description = "dev-experiment/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "dev-experiment-prod" {
  depends_on = [
    aws_api_gateway_integration.dev-experiment1-api-integration,
    aws_api_gateway_integration.dev-experiment2-api-integration,
    aws_api_gateway_integration.dev-experiment3-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.dev-experiment-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "dev-experiment-key" {
  name = "dev-experiment-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "dev-experiment" {
  name         = "dev-experiment-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.dev-experiment-api.id
    stage  = aws_api_gateway_deployment.dev-experiment-prod.stage_name
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
resource "aws_api_gateway_usage_plan_key" "dev-experiment" {
  key_id        = aws_api_gateway_api_key.dev-experiment-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.dev-experiment.id
}
