resource "aws_lambda_layer_version" "dev-experiment-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "dev-experiment-lambda-layer"
  compatible_runtimes = ["python3.7"]
}
