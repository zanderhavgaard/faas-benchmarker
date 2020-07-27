# create IAM role for lambdas
resource "aws_iam_role" "time-to-cold-start-twelve-threads-role" {
  name = "time-to-cold-start-twelve-threads-role"
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
  role = aws_iam_role.time-to-cold-start-twelve-threads-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "time-to-cold-start-twelve-threads-api" {
  name = "time-to-cold-start-twelve-threads"
  description = "time-to-cold-start-twelve-threads/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "time-to-cold-start-twelve-threads-prod" {
  depends_on = [
    aws_api_gateway_integration.time-to-cold-start-twelve-threads1-api-integration,
    aws_api_gateway_integration.time-to-cold-start-twelve-threads2-api-integration,
    aws_api_gateway_integration.time-to-cold-start-twelve-threads3-api-integration,
    aws_api_gateway_integration.monolith-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.time-to-cold-start-twelve-threads-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "time-to-cold-start-twelve-threads-key" {
  name = "time-to-cold-start-twelve-threads-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "time-to-cold-start-twelve-threads" {
  name         = "time-to-cold-start-twelve-threads-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.time-to-cold-start-twelve-threads-api.id
    stage  = aws_api_gateway_deployment.time-to-cold-start-twelve-threads-prod.stage_name
  }

  throttle_settings {
    burst_limit = 1000
    rate_limit  = 1000
  }
}

# attach api key to useage plan
resource "aws_api_gateway_usage_plan_key" "time-to-cold-start-twelve-threads" {
  key_id        = aws_api_gateway_api_key.time-to-cold-start-twelve-threads-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.time-to-cold-start-twelve-threads.id
}
