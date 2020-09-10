resource "aws_lambda_layer_version" "basic-weakest-link-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "basic-weakest-link-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "basic-weakest-link-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "basic-weakest-link-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}