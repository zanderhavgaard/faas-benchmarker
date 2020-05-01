# setup aws provider
provider "aws" {
  region = var.aws_datacenter_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  version = "2.51"
}

provider "null" {
  version = "2.1"
}
