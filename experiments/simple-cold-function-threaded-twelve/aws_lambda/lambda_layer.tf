resource "aws_lambda_layer_version" "simple-cold-function-threaded-twelve-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "simple-cold-function-threaded-twelve-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "simple-cold-function-threaded-twelve-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "simple-cold-function-threaded-twelve-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}