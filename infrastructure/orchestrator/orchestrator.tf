# this terraform file creates the persistent database server on digital ocean.

variable "do_token" {}
variable "orch_pub_key" {}
variable "orch_pvt_key" {}
variable "orch_ssh_fingerprint" {}

provider "digitalocean" {
  token = var.do_token
  version = "1.14"
}

resource "digitalocean_droplet" "orchestrator" {
  image = "ubuntu-18-04-x64"
  name = "orchestrator"
  region = "fra1"
  size = "512mb"
  private_networking = true
  ssh_keys = [var.orch_ssh_fingerprint]

  connection {
    user = "root"
    host = digitalocean_droplet.orchestrator.ipv4_address
    type = "ssh"
    private_key = file(var.orch_pvt_key)
    timeout = "2m"
  }

  provisioner "file" {
    source = "../../secrets/ssh_keys/experiment_servers"
    destination = "/root/.ssh/id_rsa"
  }

  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
      "chmod 600 /root/.ssh/id_rsa"
    ]
  }
}
