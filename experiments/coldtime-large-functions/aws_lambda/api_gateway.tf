# create IAM role for lambdas
resource "aws_iam_role" "coldtime-large-functions-role" {
  name = "coldtime-large-functions-role"
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
  role = aws_iam_role.coldtime-large-functions-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "coldtime-large-functions-api" {
  name = "coldtime-large-functions"
  description = "coldtime-large-functions/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "coldtime-large-functions-prod" {
  depends_on = [
    aws_api_gateway_integration.coldtime-large-functions1-api-integration,
    aws_api_gateway_integration.coldtime-large-functions2-api-integration,
    aws_api_gateway_integration.coldtime-large-functions3-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.coldtime-large-functions-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "coldtime-large-functions-key" {
  name = "coldtime-large-functions-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "coldtime-large-functions" {
  name         = "coldtime-large-functions-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.coldtime-large-functions-api.id
    stage  = aws_api_gateway_deployment.coldtime-large-functions-prod.stage_name
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
resource "aws_api_gateway_usage_plan_key" "coldtime-large-functions" {
  key_id        = aws_api_gateway_api_key.coldtime-large-functions-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.coldtime-large-functions.id
}
