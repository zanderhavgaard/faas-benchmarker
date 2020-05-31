resource "aws_lambda_layer_version" "growing-load-spikes-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "growing-load-spikes-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "growing-load-spikes-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "growing-load-spikes-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}