
# creates zip archive containing lambda code
data "archive_file" "growing-load-spikes3-lambda-code" {
  type = "zip"
  source_file = "${var.path_to_code}/function3.py"
  output_path = "${var.path_to_code}/lambda3.zip"
}

# create API endpoint
resource "aws_api_gateway_resource" "growing-load-spikes3-api-resource" {
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-api.id
  parent_id = aws_api_gateway_rest_api.growing-load-spikes-api.root_resource_id
  path_part = aws_lambda_function.growing-load-spikes3-python.function_name
}

# create API endpoint method
resource "aws_api_gateway_method" "growing-load-spikes3-lambda-method" {
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-api.id
  resource_id = aws_api_gateway_resource.growing-load-spikes3-api-resource.id
  http_method = "POST"
  authorization = "None"
  api_key_required = true
}

resource "aws_api_gateway_method_response" "growing-load-spikes2-response_200" {
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-api.id
  resource_id = aws_api_gateway_resource.growing-load-spikes3-api-resource.id
  http_method = aws_api_gateway_method.growing-load-spikes3-lambda-method.http_method
  status_code = "200"
}

# point API endpoint at lambda function
resource "aws_api_gateway_integration" "growing-load-spikes3-api-integration" {
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-api.id
  resource_id = aws_api_gateway_method.growing-load-spikes3-lambda-method.resource_id
  http_method = aws_api_gateway_method.growing-load-spikes3-lambda-method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.growing-load-spikes3-python.invoke_arn
}

resource "aws_api_gateway_integration_response" "growing-load-spikes3" {
  depends_on = [
    aws_api_gateway_integration.growing-load-spikes3-api-integration
  ]
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-api.id
  resource_id = aws_api_gateway_method.growing-load-spikes3-lambda-method.resource_id
  http_method = aws_api_gateway_method.growing-load-spikes3-lambda-method.http_method
  status_code = aws_api_gateway_method_response.growing-load-spikes2-response_200.status_code
}

# add permission for gateway to invoke lambdas
resource "aws_lambda_permission" "growing-load-spikes3-apigw-permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.growing-load-spikes3-python.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.growing-load-spikes-api.execution_arn}/*/*"
}

# create lambda function
resource "aws_lambda_function" "growing-load-spikes3-python" {
  filename = data.archive_file.growing-load-spikes3-lambda-code.output_path
  function_name = "growing-load-spikes-function3"
  role = aws_iam_role.growing-load-spikes-role.arn
  handler = "function3.lambda_handler"
  runtime = "python3.7"
  source_code_hash = filesha256(data.archive_file.growing-load-spikes3-lambda-code.output_path)
  publish = true
  layers = [aws_lambda_layer_version.growing-load-spikes-lambda-layer.arn]
  timeout = 10
}
