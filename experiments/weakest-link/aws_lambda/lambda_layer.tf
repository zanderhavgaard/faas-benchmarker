resource "aws_lambda_layer_version" "weakest-link-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "weakest-link-lambda-layer"
  compatible_runtimes = ["python3.7"]
}
