# create linux vm
resource "azurerm_linux_virtual_machine" "scenario-pyramid-worker" {
  depends_on = [azurerm_network_interface.scenario-pyramid-worker-ni]

  name                = "scenario-pyramid-worker"
  resource_group_name = azurerm_resource_group.scenario-pyramid-worker-rg.name
  location            = azurerm_resource_group.scenario-pyramid-worker-rg.location
  size                = "Standard_B1s"
  admin_username      = "ubuntu"
  disable_password_authentication = true
  network_interface_ids = [
    azurerm_network_interface.scenario-pyramid-worker-ni.id,
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

# HACK to run provisioners over SSH after instance
# has been created and recieved a public ip address
resource "null_resource" "linux-provisioners" {
  # run the provisioners after the instance has been created
  # and the ip address has been assigned
  depends_on = [
    azurerm_linux_virtual_machine.scenario-pyramid-worker,
    azurerm_public_ip.scenario-pyramid-worker-public-ip
  ]

  # setup ssh connection for provisioners
  connection {
    user = "ubuntu"
    host = azurerm_linux_virtual_machine.scenario-pyramid-worker.public_ip_address
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
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",

      "chmod 600 /home/ubuntu/.ssh/id_rsa",
      "{ echo -n 'export fbrd=/home/ubuntu/faas-benchmarker\n' ; echo -n 'export PYTHONPATH=$PYTHONPATH:/home/ubuntu/faas-benchmarker/benchmark\n' ; echo -n 'export DB_HOSTNAME=${var.db_server_static_ip}\n' ; cat .bashrc ; } > /home/ubuntu/.bashrc.new",
      "mv .bashrc.new .bashrc",

      "sudo apt-get update -q",
      "sudo apt-get install -qq docker-compose",
      "sudo systemctl enable --now docker",
      "sudo usermod -aG docker ubuntu",
      "sudo docker pull -q faasbenchmarker/client:latest"
    ]
  }
}
