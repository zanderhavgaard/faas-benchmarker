

# creates zip archive containing lambda code
data "archive_file" "monolith-lambda-code" {
  type = "zip"
  source_file = "${var.path_to_code}/monolith.py"
  output_path = "${var.path_to_code}/monolith.zip"
}

# create API endpoint
resource "aws_api_gateway_resource" "monolith-api-resource" {
  rest_api_id = aws_api_gateway_rest_api.basic-weakest-link-api.id
  parent_id = aws_api_gateway_rest_api.basic-weakest-link-api.root_resource_id
  path_part = aws_lambda_function.monolith-python.function_name
}

# create API endpoint method
resource "aws_api_gateway_method" "monolith-lambda-method" {
  rest_api_id = aws_api_gateway_rest_api.basic-weakest-link-api.id
  resource_id = aws_api_gateway_resource.monolith-api-resource.id
  http_method = "POST"
  authorization = "None"
  api_key_required = true
}

resource "aws_api_gateway_method_response" "monolith-response_200" {
  rest_api_id = aws_api_gateway_rest_api.basic-weakest-link-api.id
  resource_id = aws_api_gateway_resource.monolith-api-resource.id
  http_method = aws_api_gateway_method.monolith-lambda-method.http_method
  status_code = "200"
}

# point API endpoint at lambda function
resource "aws_api_gateway_integration" "monolith-api-integration" {
  rest_api_id = aws_api_gateway_rest_api.basic-weakest-link-api.id
  resource_id = aws_api_gateway_method.monolith-lambda-method.resource_id
  http_method = aws_api_gateway_method.monolith-lambda-method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.monolith-python.invoke_arn
}

resource "aws_api_gateway_integration_response" "monolith" {
  depends_on = [
    aws_api_gateway_integration.monolith-api-integration
  ]
  rest_api_id = aws_api_gateway_rest_api.basic-weakest-link-api.id
  resource_id = aws_api_gateway_method.monolith-lambda-method.resource_id
  http_method = aws_api_gateway_method.monolith-lambda-method.http_method
  status_code = aws_api_gateway_method_response.monolith-response_200.status_code
}

# add permission for gateway to invoke lambdas
resource "aws_lambda_permission" "monolith-apigw-permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.monolith-python.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.basic-weakest-link-api.execution_arn}/*/*"
}

# create lambda function
resource "aws_lambda_function" "monolith-python" {
  filename = data.archive_file.monolith-lambda-code.output_path
  function_name = "basic-weakest-link-monolith"
  role = aws_iam_role.basic-weakest-link-role.arn
  handler = "monolith.lambda_handler"
  runtime = "python3.7"
  source_code_hash = filesha256(data.archive_file.monolith-lambda-code.output_path)
  publish = true
  layers = [aws_lambda_layer_version.basic-weakest-link-monolith-lambda-layer.arn]
  timeout = 60
}
