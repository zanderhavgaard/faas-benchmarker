# this terraform file creates the persistent database server on digital ocean.

variable "do_token" {}
variable "db_pub_key" {}
variable "db_pvt_key" {}
variable "db_ssh_fingerprint" {}
variable "client_ssh_fingerprint" {}
variable "orch_ssh_fingerprint" {}

provider "digitalocean" {
  token = var.do_token
  version = "1.14"
}

resource "digitalocean_droplet" "db-server" {
  image = "docker-18-04"
  name = "db-server"
  region = "fra1"
  size = "512mb"
  private_networking = true
  ssh_keys = [var.db_ssh_fingerprint, var.client_ssh_fingerprint, var.orch_ssh_fingerprint]

  connection {
    user = "root"
    host = digitalocean_droplet.db-server.ipv4_address
    type = "ssh"
    private_key = file(var.db_pvt_key)
    timeout = "2m"
  }

  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
      "cd /root",
      "git clone https://github.com/zanderhavgaard/faas-benchmarker",
      "cd faas-benchmarker"
    ]
  }
}

# output ip address
output "ip_address" {
  value = digitalocean_droplet.db-server.ipv4_address
}
