resource "aws_lambda_layer_version" "concurrency-benchmarking-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "concurrency-benchmarking-lambda-layer"
  compatible_runtimes = ["python3.7"]
}
