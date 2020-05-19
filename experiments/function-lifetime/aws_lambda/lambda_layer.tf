resource "aws_lambda_layer_version" "function-lifetime-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "function-lifetime-lambda-layer"
  compatible_runtimes = ["python3.7"]
}
