# see https://docs.microsoft.com/en-us/azure/terraform/terraform-install-configure
# and https://www.terraform.io/docs/providers/azurerm/guides/service_principal_client_secret.html
# on how to get up and running

# template for creating azure experiment worker vm
# based on: https://www.terraform.io/docs/providers/azurerm/r/linux_virtual_machine.html
# and: https://docs.microsoft.com/en-us/azure/terraform/terraform-create-complete-vm

# you must supply the experiment context as a command line argument
variable "remote_env_file" {}
variable "env_file" {}

# import variables
variable "subscription_id" {}
variable "client_id" {}
variable "client_secret" {}
variable "tenant_id" {}

# ssh key vars
variable "client_pub_key" {}
variable "client_pvt_key" {}
variable "client_ssh_fingerprint" {}

# setup provider
provider "azurerm" {
  subscription_id = var.subscription_id
  client_id = var.client_id
  client_secret = var.client_secret
  tenant_id = var.tenant_id
  version = "2.0"
  features {}
}

provider "null" {
  version = "2.1"
}

# create resource group
resource "azurerm_resource_group" "changeme-worker-rg" {
  name     = "changeme-worker"
  location = "West Europe"
}

# create VPC
resource "azurerm_virtual_network" "changeme-worker-network" {
  name                = "changeme-worker-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.changeme-worker-rg.location
  resource_group_name = azurerm_resource_group.changeme-worker-rg.name
}

# create subnet
resource "azurerm_subnet" "changeme-worker-subnet" {
  name                 = "changeme-worker-subnet"
  resource_group_name  = azurerm_resource_group.changeme-worker-rg.name
  virtual_network_name = azurerm_virtual_network.changeme-worker-network.name
  address_prefix       = "10.0.2.0/24"
}

# create network interface
resource "azurerm_network_interface" "changeme-worker-ni" {
  name                = "changeme-worker-nic"
  location            = azurerm_resource_group.changeme-worker-rg.location
  resource_group_name = azurerm_resource_group.changeme-worker-rg.name

  ip_configuration {
    name                          = "changeme-worker-ip-config"
    subnet_id                     = azurerm_subnet.changeme-worker-subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id = azurerm_public_ip.changeme-worker-public-ip.id
  }
}

# create public ip address
resource "azurerm_public_ip" "changeme-worker-public-ip" {
  name = "changeme-worker-public-ip"
  location = azurerm_resource_group.changeme-worker-rg.location
  resource_group_name = azurerm_resource_group.changeme-worker-rg.name
  allocation_method = "Dynamic"
}

# create linux vm
resource "azurerm_linux_virtual_machine" "changeme-worker" {
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

# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.changeme-worker.public_ip_address
}
