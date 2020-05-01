# connect to the openfaas instance
variable "openfaas_uri" {}
variable "openfaas_password" {}
variable "openfaas_username" {
  type = string
  default = "admin"
}

# the hub.docker.com username that has the images
variable "dockerhub_username" {
  type = string
  default = "zanderhavgaard"
}

provider "openfaas" {
  version = "~> 0.3"
  uri = var.openfaas_uri
  user_name = var.openfaas_username
  password = var.openfaas_password
}
