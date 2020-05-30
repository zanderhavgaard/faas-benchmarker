resource "aws_lambda_layer_version" "coldtime-large-functions-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "coldtime-large-functions-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "coldtime-large-functions-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "coldtime-large-functions-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}