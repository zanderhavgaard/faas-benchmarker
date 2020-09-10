# create IAM role for lambdas
resource "aws_iam_role" "basic-weakest-link-role" {
  name = "basic-weakest-link-role"
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
  role = aws_iam_role.basic-weakest-link-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "basic-weakest-link-api" {
  name = "basic-weakest-link"
  description = "basic-weakest-link/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "basic-weakest-link-prod" {
  depends_on = [
    aws_api_gateway_integration.basic-weakest-link1-api-integration,
    aws_api_gateway_integration.basic-weakest-link2-api-integration,
    aws_api_gateway_integration.basic-weakest-link3-api-integration,
    aws_api_gateway_integration.monolith-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.basic-weakest-link-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "basic-weakest-link-key" {
  name = "basic-weakest-link-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "basic-weakest-link" {
  name         = "basic-weakest-link-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.basic-weakest-link-api.id
    stage  = aws_api_gateway_deployment.basic-weakest-link-prod.stage_name
  }

  throttle_settings {
    burst_limit = 1000
    rate_limit  = 1000
  }
}

# attach api key to useage plan
resource "aws_api_gateway_usage_plan_key" "basic-weakest-link" {
  key_id        = aws_api_gateway_api_key.basic-weakest-link-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.basic-weakest-link.id
}
