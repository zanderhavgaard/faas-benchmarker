resource "aws_lambda_layer_version" "linear-invocation-nested-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "linear-invocation-nested-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "linear-invocation-nested-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "linear-invocation-nested-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}