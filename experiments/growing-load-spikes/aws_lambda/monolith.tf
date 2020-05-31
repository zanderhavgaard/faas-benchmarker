
# creates zip archive containing lambda code
data "archive_file" "growing-load-spikes-monolith-lambda-code" {
  type = "zip"
  source_file = "${var.path_to_code}/growing-load-spikes-monolith.py"
  output_path = "${var.path_to_code}/growing-load-spikes-monolith.zip"
}

# create API endpoint
resource "aws_api_gateway_resource" "growing-load-spikes-monolith-api-resource" {
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-monolith-api.id
  parent_id = aws_api_gateway_rest_api.growing-load-spikes-monolith-api.root_resource_id
  path_part = "growing-load-spikes-monolith"
}

# create API endpoint method
resource "aws_api_gateway_method" "growing-load-spikes-monolith-lambda-method" {
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-monolith-api.id
  resource_id = aws_api_gateway_resource.growing-load-spikes-monolith-api-resource.id
  http_method = "POST"
  authorization = "None"
  api_key_required = true
}

resource "aws_api_gateway_method_response" "growing-load-spikes-monolith-response_200" {
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-monolith-api.id
  resource_id = aws_api_gateway_resource.growing-load-spikes-monolith-api-resource.id
  http_method = aws_api_gateway_method.growing-load-spikes-monolith-lambda-method.http_method
  status_code = "200"
}

# point API endpoint at lambda function
resource "aws_api_gateway_integration" "growing-load-spikes-monolith-api-integration" {
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-monolith-api.id
  resource_id = aws_api_gateway_method.growing-load-spikes-monolith-lambda-method.resource_id
  http_method = aws_api_gateway_method.growing-load-spikes-monolith-lambda-method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.growing-load-spikes-monolith-python.invoke_arn
}

resource "aws_api_gateway_integration_response" "growing-load-spikes-monolith" {
  depends_on = [
    aws_api_gateway_integration.growing-load-spikes-monolith-api-integration
  ]
  rest_api_id = aws_api_gateway_rest_api.growing-load-spikes-monolith-api.id
  resource_id = aws_api_gateway_method.growing-load-spikes-monolith-lambda-method.resource_id
  http_method = aws_api_gateway_method.growing-load-spikes-monolith-lambda-method.http_method
  status_code = aws_api_gateway_method_response.growing-load-spikes-monolith-response_200.status_code
}

# add permission for gateway to invoke lambdas
resource "aws_lambda_permission" "growing-load-spikes-monolith-apigw-permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.growing-load-spikes-monolith-python.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.growing-load-spikes-monolith-api.execution_arn}/*/*"
}

# create lambda function
resource "aws_lambda_function" "growing-load-spikes-monolith-python" {
  filename = data.archive_file.growing-load-spikes-monolith-lambda-code.output_path
  function_name = "monolith"
  role = aws_iam_role.growing-load-spikes-monolith-role.arn
  handler = "monolith.lambda_handler"
  runtime = "python3.7"
  source_code_hash = filesha256(data.archive_file.growing-load-spikes-growing-load-spikes-monolith-lambda-code.output_path)
  publish = true
  layers = [aws_lambda_layer_version.growing-load-spikes-growing-load-spikes-monolith-lambda-layer.arn]
}
