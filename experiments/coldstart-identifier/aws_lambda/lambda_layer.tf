resource "aws_lambda_layer_version" "coldstart-identifier-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "coldstart-identifier-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "coldstart-identifier-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "coldstart-identifier-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}