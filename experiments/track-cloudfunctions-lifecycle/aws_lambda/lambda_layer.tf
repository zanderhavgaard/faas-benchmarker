resource "aws_lambda_layer_version" "track-cloudfunctions-lifecycle-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer.zip"
  layer_name = "track-cloudfunctions-lifecycle-lambda-layer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "track-cloudfunctions-lifecycle-monolith-lambda-layer" {
  filename = "${var.path_to_code}/lambda_layer_monolith.zip"
  layer_name = "track-cloudfunctions-lifecycle-monolith-lambda-layer"
  compatible_runtimes = ["python3.7"]
}