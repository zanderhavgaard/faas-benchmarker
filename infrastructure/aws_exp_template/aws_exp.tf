# this terraform file creates the persistent database server on digital ocean.

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "exp_pub_key" {}
variable "exp_pvt_key" {}
variable "exp_ssh_fingerprint" {}

provider "aws" {
  region = "eu-central-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

resource "digitalocean_droplet" "experiment-worker-aws" {
  image = "ubuntu-18-04-x64"
  name = "experiment-worker-aws"
  region = "fra1"
  size = "512mb"
  private_networking = true
  ssh_keys = [var.orch_ssh_fingerprint]

  connection {
    user = "root"
    host = digitalocean_droplet.experiment-worker-aws.ipv4_address
    type = "ssh"
    private_key = file(var.orch_pvt_key)
    timeout = "2m"
  }

  # get the key to connect to db server
  provisioner "file" {
    source = "../../secrets/ssh_keys/db_server"
    destination = "/root/.ssh/id_rsa"
  }

  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
      "chmod 600 /root/.ssh/id_rsa"
    ]
  }
}
