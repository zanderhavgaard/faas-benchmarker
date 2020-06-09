resource "aws_lambda_layer_version" "single-function-time-to-cold-start-multithreaded-twelve-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "single-function-time-to-cold-start-multithreaded-twelve-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "single-function-time-to-cold-start-multithreaded-twelve-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "single-function-time-to-cold-start-multithreaded-twelve-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}