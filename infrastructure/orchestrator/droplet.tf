resource "digitalocean_droplet" "orchestrator" {
  image = "ubuntu-19-10-x64"
  # image = "ubuntu-20-04-x64"
  name = "orchestrator"
  region = "fra1"
  size = "s-2vcpu-2gb"
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
    source = "../../secrets/ssh_keys/experiment_servers"
    destination = "/root/experiment_servers"
  }
  provisioner "file" {
    source = "../../secrets/ssh_keys/experiment_servers.pub"
    destination = "/root/experiment_servers.pub"
  }
  provisioner "file" {
    source = "../../secrets/terraform_env/terraform_env"
    destination = "/root/terraform_env"
  }
  provisioner "file" {
    source = "../../secrets/openfaas_orchestration_credentials/config"
    destination = "/root/config"
  }
  provisioner "file" {
    source = "../../secrets/openfaas_orchestration_credentials/credentials"
    destination = "/root/credentials"
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
      "apt-get install -qq zsh fzf neovim figlet unzip git python3 python3-dev python3-pip",
      "apt-get autoremove -qq",

      # enable docker
      # "systemctl enbale --now docker",
      # "sudo usermod -aG docker ubuntu",

      # install terraform v. 0.12.24
      "wget https://releases.hashicorp.com/terraform/0.12.26/terraform_0.12.26_linux_amd64.zip",
      "unzip terraform_0.12.26_linux_amd64.zip",
      "rm terraform_0.12.26_linux_amd64.zip",
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
      "echo 'export PYTHON_PATH=\"$PYTHON_PATH:$fbrd/benchmark\"' >> /home/ubuntu/.bashrc",
      "echo 'cd /home/ubuntu/faas-benchmarker && git pull' >> /home/ubuntu/.bashrc",
      "echo 'export FUNCTIONS_CORE_TOOLS_TELEMETRY_OPTOUT=1' >> /home/ubuntu/.bashrc",
      "echo 'alias tailf=\"tail -f -n 999999\"' >> /home/ubuntu/.bashrc",

      # install azure functions cli tools
      "curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg",
      "mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg",
      "sh -c 'echo \"deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main\" > /etc/apt/sources.list.d/dotnetdev.list'",
      "apt-get update -q",
      "apt-get install -qq azure-functions-core-tools",

      # install azure cli
      "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash",
      # login to azure cli
      "az login --service-principal -u ${var.client_id} -p ${var.client_secret} --tenant ${var.tenant_id}",
      "mv /root/.azure /home/ubuntu/.azure",

      # add environment vars to new user
      "echo 'source /home/ubuntu/terraform_env' >> /home/ubuntu/.bashrc",

      # clone repository
      "git clone --quiet https://github.com/zanderhavgaard/faas-benchmarker /home/ubuntu/faas-benchmarker",
      # move the secrets directory the correct location
      "mkdir -pv /home/ubuntu/faas-benchmarker/secrets/ssh_keys",
      "mv /root/experiment_servers /home/ubuntu/faas-benchmarker/secrets/ssh_keys/experiment_servers",
      "mv /root/experiment_servers.pub /home/ubuntu/faas-benchmarker/secrets/ssh_keys/experiment_servers.pub",
      "chmod 600 /home/ubuntu/faas-benchmarker/secrets/ssh_keys/experiment_servers",
      "chmod 644 /home/ubuntu/faas-benchmarker/secrets/ssh_keys/experiment_servers.pub",

      # move eks/aws credentials
      "mkdir -pv /home/ubuntu/faas-benchmarker/secrets/openfaas_orchestration_credentials",
      "mv /root/config /home/ubuntu/faas-benchmarker/secrets/openfaas_orchestration_credentials/config",
      "mv /root/credentials /home/ubuntu/faas-benchmarker/secrets/openfaas_orchestration_credentials/credentials",


      # make sure ubuntu owns all of it's stuff...
      "chown -R \"ubuntu:ubuntu\" /home/ubuntu",

      "echo ======================================",
      "echo = Done setting up orchstrator server =",
      "echo ======================================",

    ]
  }

}
