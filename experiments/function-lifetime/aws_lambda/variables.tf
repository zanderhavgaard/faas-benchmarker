variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_datacenter_region" {}

# path to lambda function code
variable "path_to_code" {
  type = string
  default = "../../../cloud_functions/aws_lambda"
}

# loacal variables
locals {
  aws_region = "eu-central-1"
}
