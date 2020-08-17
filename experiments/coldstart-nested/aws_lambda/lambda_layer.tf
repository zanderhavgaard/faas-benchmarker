resource "aws_lambda_layer_version" "coldstart-nested-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "coldstart-nested-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "coldstart-nested-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "coldstart-nested-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}