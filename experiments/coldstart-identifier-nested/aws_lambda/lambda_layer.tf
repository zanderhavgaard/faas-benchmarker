resource "aws_lambda_layer_version" "coldstart-identifier-nested-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "coldstart-identifier-nested-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "coldstart-identifier-nested-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "coldstart-identifier-nested-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}