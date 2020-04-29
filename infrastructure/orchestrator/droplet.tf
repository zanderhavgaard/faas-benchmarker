resource "digitalocean_droplet" "orchestrator" {
  image = "ubuntu-18-04-x64"
  name = "orchestrator"
  region = "fra1"
  size = "s-1vcpu-1gb"
  private_networking = true
  ssh_keys = [var.orch_ssh_fingerprint]
}

resource "random_password" "password" {
  length = 50
}

resource "null_resource" "root-provisioner" {
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
      # wait for cloud-init to finish
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",

      # configure firewall
      "ufw default allow outgoing",
      "ufw default deny incoming",
      "ufw allow ssh",
      "ufw --force enable",
      "systemctl enable ufw",

      # set permissions for experiment servers key
      "chmod 600 /root/.ssh/id_rsa",

      # install stuff
      "apt-get update -q",
      "apt-get upgrade -qq",
      # there might be more updates dependent on the first batch of updates...
      "apt-get update -q",
      "apt-get upgrade -qq",
      "apt-get install -y -qq figlet unzip git python3 python3-dev python3-pip",

      # install terraform v. 0.12.24
      "wget https://releases.hashicorp.com/terraform/0.12.24/terraform_0.12.24_linux_amd64.zip",
      "unzip terraform_0.12.24_linux_amd64.zip",
      "rm terraform_0.12.24_linux_amd64.zip",
      "mv terraform /usr/bin/terraform",

      # setup non root user
      "useradd --create-home --shell /bin/bash ${var.username}",
      "echo \"${var.username}:${random_password.password.result}\" | chpasswd",
      "mkdir /home/ubuntu/.ssh",
      "cp /root/.ssh/* /home/ubuntu/.ssh/",
      # TODO maybe uncomment
      # "rm -rf /root/.ssh",
      "mv /root/terraform_env /home/ubuntu/terraform_env",
      "echo \"figlet 'orchestrator'\" >> /home/ubuntu/.bashrc",

      # install azure cli
      "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash",
      # login to azure cli
      "az login --service-principal -u ${var.client_id} -p ${var.client_secret} --tenant ${var.tenant_id}",
      "mv /root/.azure /home/ubuntu/.azure",

      # add environment vars to new user
      "echo 'source /home/ubuntu/terraform_env' >> /home/ubuntu/.bashrc",

      # clone repository
      "git clone --quiet https://github.com/zanderhavgaard/faas-benchmarker /home/ubuntu/faas-benchmarker",

      # make sure ubuntu owns all of it's stuff...
      "chown -R \"ubuntu:ubuntu\" /home/ubuntu",

      "echo ======================================",
      "echo = Done setting up orchstrator server =",
      "echo ======================================",

      # reboot to apply any kernel updates
      "reboot &",
    ]
  }

}
