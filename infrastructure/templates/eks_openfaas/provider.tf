# setup AWS Provider

variable "aws_access_key" {}
variable "aws_secret_key" {}

# setup aws provider
provider "aws" {
  region = "eu-central-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  version = "2.51"
}
