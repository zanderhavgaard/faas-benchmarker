# create IAM role for lambdas
resource "aws_iam_role" "track-cloudfunctions-lifecycle-role" {
  name = "track-cloudfunctions-lifecycle-role"
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
  role = aws_iam_role.track-cloudfunctions-lifecycle-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}

# create API gateway
resource "aws_api_gateway_rest_api" "track-cloudfunctions-lifecycle-api" {
  name = "track-cloudfunctions-lifecycle"
  description = "track-cloudfunctions-lifecycle/test environment"
}

# add a deployment of the api
resource "aws_api_gateway_deployment" "track-cloudfunctions-lifecycle-prod" {
  depends_on = [
    aws_api_gateway_integration.track-cloudfunctions-lifecycle1-api-integration,
    aws_api_gateway_integration.track-cloudfunctions-lifecycle2-api-integration,
    aws_api_gateway_integration.track-cloudfunctions-lifecycle3-api-integration,
    aws_api_gateway_integration.monolith-api-integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.track-cloudfunctions-lifecycle-api.id
  stage_name = "prod"
}

# create api useage plan key
resource "aws_api_gateway_api_key" "track-cloudfunctions-lifecycle-key" {
  name = "track-cloudfunctions-lifecycle-key"
}

# create api usage plan
resource "aws_api_gateway_usage_plan" "track-cloudfunctions-lifecycle" {
  name         = "track-cloudfunctions-lifecycle-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.track-cloudfunctions-lifecycle-api.id
    stage  = aws_api_gateway_deployment.track-cloudfunctions-lifecycle-prod.stage_name
  }

  throttle_settings {
    burst_limit = 1000
    rate_limit  = 1000
  }
}

# attach api key to useage plan
resource "aws_api_gateway_usage_plan_key" "track-cloudfunctions-lifecycle" {
  key_id        = aws_api_gateway_api_key.track-cloudfunctions-lifecycle-key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.track-cloudfunctions-lifecycle.id
}
