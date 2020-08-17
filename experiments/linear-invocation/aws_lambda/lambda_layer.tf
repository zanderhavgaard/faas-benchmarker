resource "aws_lambda_layer_version" "linear-invocation-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "linear-invocation-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "linear-invocation-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "linear-invocation-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}