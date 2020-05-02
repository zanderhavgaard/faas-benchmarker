# create linux vm
resource "azurerm_linux_virtual_machine" "changeme-worker" {
  depends_on = [azurerm_network_interface.changeme-worker-ni]

  name                = "changeme-worker"
  resource_group_name = azurerm_resource_group.changeme-worker-rg.name
  location            = azurerm_resource_group.changeme-worker-rg.location
  size                = "Standard_B1s"
  admin_username      = "ubuntu"
  disable_password_authentication = true
  network_interface_ids = [
    azurerm_network_interface.changeme-worker-ni.id,
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
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }
}

# HACK to run provisioners over SSH after instance
# has been created and recieved a public ip address
resource "null_resource" "linux-provisioners" {
  # run the provisioners after the instance has been created
  # and the ip address has been assigned
  depends_on = [
    azurerm_linux_virtual_machine.changeme-worker,
    azurerm_public_ip.changeme-worker-public-ip
  ]

  # setup ssh connection for provisioners
  connection {
    user = "ubuntu"
    host = azurerm_linux_virtual_machine.changeme-worker.public_ip_address
    type = "ssh"
    private_key = file(var.client_pvt_key)
    timeout = "2m"
  }

  provisioner "file" {
    source = "../../../secrets/ssh_keys/experiment_servers"
    destination = "/home/ubuntu/.ssh/id_rsa"
  }

  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",
      "sudo apt-get update -q",
      "sudo apt-get install -y -qq git python3 python3-dev python3-pip",
      "git clone --quiet https://github.com/zanderhavgaard/faas-benchmarker /home/ubuntu/faas-benchmarker",
      "{ echo -n 'export fbrd=/home/ubuntu/faas-benchmarker\n' ; echo -n 'export PYTHONPATH=$PYTHONPATH:/home/ubuntu/faas-benchmarker/benchmark\n' ; cat .bashrc ; } > /home/ubuntu/.bashrc.new",
      "mv .bashrc.new .bashrc",
      "cd /home/ubuntu/faas-benchmarker",
      "pip3 install -q -r requirements.txt",
    ]
  }

  # copy local files to remote server
  # useage: https://www.terraform.io/docs/provisioners/file.html
  provisioner "file" {
    source = var.env_file
    destination = var.remote_env_file
  }
}
