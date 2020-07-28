# create linux vm
resource "azurerm_linux_virtual_machine" "simple-cold-function-openfaas-worker" {
  depends_on = [azurerm_network_interface.simple-cold-function-openfaas-worker-ni]

  name                = "simple-cold-function-openfaas-worker"
  resource_group_name = azurerm_resource_group.simple-cold-function-openfaas-worker-rg.name
  location            = azurerm_resource_group.simple-cold-function-openfaas-worker-rg.location
  size                = var.openfaas_client_vm_size
  admin_username      = "ubuntu"
  disable_password_authentication = true
  network_interface_ids = [
    azurerm_network_interface.simple-cold-function-openfaas-worker-ni.id,
  ]

  admin_ssh_key {
    username   = "ubuntu"
    public_key = file(var.client_pub_key)
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-minimal-focal-daily"
    sku       = "minimal-20_04-daily-lts"
    version   = "latest"
  }
}

# Run provisioners over SSH after instance
# has been created and recieved a public ip address
resource "null_resource" "linux-provisioners" {
  # run the provisioners after the instance has been created
  # and the ip address has been assigned
  depends_on = [
    azurerm_linux_virtual_machine.simple-cold-function-openfaas-worker,
    azurerm_public_ip.simple-cold-function-openfaas-worker-public-ip
  ]

  # setup ssh connection for provisioners
  connection {
    user = "ubuntu"
    host = azurerm_linux_virtual_machine.simple-cold-function-openfaas-worker.public_ip_address
    type = "ssh"
    private_key = file(var.client_pvt_key)
    timeout = "2m"
  }

  provisioner "file" {
    source = "../../../secrets/ssh_keys/experiment_servers"
    destination = "/home/ubuntu/.ssh/id_rsa"
  }
  provisioner "file" {
    source = var.env_file
    destination = var.remote_env_file
  }

  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      # wait for cloud-init to finish
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",
      # set permission for private key
      "chmod 600 /home/ubuntu/.ssh/id_rsa",
      # set some environment variables
      "{ echo -n 'export fbrd=/home/ubuntu/faas-benchmarker\n' ; echo -n 'export PYTHONPATH=$PYTHONPATH:/home/ubuntu/faas-benchmarker/benchmark\n' ; echo -n 'export DB_HOSTNAME=${var.db_server_static_ip}\n' ; cat .bashrc ; } > /home/ubuntu/.bashrc.new",
      "mv .bashrc.new .bashrc",

      # install docker and other tools
      "sudo apt-get update -q",
      "sudo apt-get install -y -qq moreutils unzip git python3 python3-dev python3-venv docker-compose",
      "sudo systemctl enable --now docker",
      "sudo usermod -aG docker ubuntu",
      "sudo docker pull -q faasbenchmarker/client:latest",

      # clone repo
      "git clone --quiet https://github.com/zanderhavgaard/faas-benchmarker /home/ubuntu/faas-benchmarker",

      # install depenencies for creating the openfaas cluster
      "bash /home/ubuntu/faas-benchmarker/eks_openfaas_orchestration/install_openfaas_orchestration_tools.sh",
      # create directory for aws credentials
      "mkdir /home/ubuntu/.aws",
    ]
  }

  # copy AWS credentials to enable creating the EKS cluster for OpenFaas
  provisioner "file" {
    source = "../../../secrets/openfaas_orchestration_credentials/"
    destination = "/home/ubuntu/.aws"
  }
}
