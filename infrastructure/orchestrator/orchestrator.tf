# this terraform file creates the master orchestrator server on digital ocean.

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

  provisioner "file" {
    source = "../../secrets/terraform_env/terraform_env"
    destination = "/root/terraform_env"
  }

  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
      # set permissions for experiment servers key
      "chmod 600 /root/.ssh/id_rsa",

      # source terraform env file
      "echo 'source /root/terraform_env' >> .bashrc",

      # clone repository
      "git clone https://github.com/zanderhavgaard/thesis-code",

      # install terraform v. 0.12.21
      "apt update",
      "apt install -y unzip",
      "wget https://releases.hashicorp.com/terraform/0.12.21/terraform_0.12.21_linux_amd64.zip",
      "unzip terraform_0.12.21_linux_amd64.zip",
      "rm terraform_0.12.21_linux_amd64.zip",
      "mv terraform /usr/bin/terraform",

      "echo ======================================",
      "echo = Done setting up orchstrator server =",
      "echo ======================================",
    ]
  }
}

# output ip address
output "ip_address" {
  value = digitalocean_droplet.orchestrator.ipv4_address
}
