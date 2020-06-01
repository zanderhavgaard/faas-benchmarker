resource "aws_lambda_layer_version" "scenario-pyramid-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "scenario-pyramid-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "scenario-pyramid-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "scenario-pyramid-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}