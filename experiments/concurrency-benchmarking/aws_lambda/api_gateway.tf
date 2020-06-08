# create IAM role for lambdas
resource "aws_iam_role" "concurrency-benchmarking-role" {
  name = "concurrency-benchmarking-role"
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
  role = aws_iam_role.concurrency-benchmarking-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "concurrency-benchmarking-api" {
  name = "concurrency-benchmarking"
  description = "concurrency-benchmarking/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "concurrency-benchmarking-prod" {
  depends_on = [
    aws_api_gateway_integration.concurrency-benchmarking1-api-integration,
    aws_api_gateway_integration.concurrency-benchmarking2-api-integration,
    aws_api_gateway_integration.concurrency-benchmarking3-api-integration,
    aws_api_gateway_integration.monolith-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.concurrency-benchmarking-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "concurrency-benchmarking-key" {
  name = "concurrency-benchmarking-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "concurrency-benchmarking" {
  name         = "concurrency-benchmarking-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.concurrency-benchmarking-api.id
    stage  = aws_api_gateway_deployment.concurrency-benchmarking-prod.stage_name
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
resource "aws_api_gateway_usage_plan_key" "concurrency-benchmarking" {
  key_id        = aws_api_gateway_api_key.concurrency-benchmarking-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.concurrency-benchmarking.id
}
