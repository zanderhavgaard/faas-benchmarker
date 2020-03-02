# see https://docs.microsoft.com/en-us/azure/terraform/terraform-install-configure
# and https://www.terraform.io/docs/providers/azurerm/guides/service_principal_client_secret.html
# on how to get up and running

# template for creating azure experiment worker vm
# based on: https://www.terraform.io/docs/providers/azurerm/r/linux_virtual_machine.html
# and: https://docs.microsoft.com/en-us/azure/terraform/terraform-create-complete-vm

# import variables
variable "subscription_id" {}
variable "client_id" {}
variable "client_secret" {}
variable "tenant_id" {}

variable "exp_pub_key" {}
variable "exp_pvt_key" {}
variable "exp_ssh_fingerprint" {}

# setup provider
provider "azurerm" {
  subscription_id = var.subscription_id
  client_id = var.client_id
  client_secret = var.client_secret
  tenant_id = var.tenant_id
  version = "2.0"
  features {}
}

# create resource group
resource "azurerm_resource_group" "azure-experiment-worker-rg" {
  name     = "azure-experiment-worker"
  location = "West Europe"
}

# create VPC
resource "azurerm_virtual_network" "azure-experiment-worker-network" {
  name                = "azure-experiment-worker-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.azure-experiment-worker-rg.location
  resource_group_name = azurerm_resource_group.azure-experiment-worker-rg.name
}

# create subnet
resource "azurerm_subnet" "azure-experiment-worker-subnet" {
  name                 = "azure-experiment-worker-subnet"
  resource_group_name  = azurerm_resource_group.azure-experiment-worker-rg.name
  virtual_network_name = azurerm_virtual_network.azure-experiment-worker-network.name
  address_prefix       = "10.0.2.0/24"
}

# create network interface
resource "azurerm_network_interface" "azure-experiment-worker-ni" {
  name                = "azure-experiment-worker-nic"
  location            = azurerm_resource_group.azure-experiment-worker-rg.location
  resource_group_name = azurerm_resource_group.azure-experiment-worker-rg.name

  ip_configuration {
    name                          = "azure-experiment-worker-ip-config"
    subnet_id                     = azurerm_subnet.azure-experiment-worker-subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id = azurerm_public_ip.azure-experiment-worker-public-ip.id
  }
}

# create public ip address
resource "azurerm_public_ip" "azure-experiment-worker-public-ip" {
  name = "azure-experiment-worker-public-ip"
  location = azurerm_resource_group.azure-experiment-worker-rg.location
  resource_group_name = azurerm_resource_group.azure-experiment-worker-rg.name
  allocation_method = "Dynamic"
}

# create linux vm
resource "azurerm_linux_virtual_machine" "azure-experiment-worker" {
  name                = "azure-experiment-worker"
  resource_group_name = azurerm_resource_group.azure-experiment-worker-rg.name
  location            = azurerm_resource_group.azure-experiment-worker-rg.location
  size                = "Standard_B1s"
  admin_username      = "ubuntu"
  disable_password_authentication = true
  network_interface_ids = [
    azurerm_network_interface.azure-experiment-worker-ni.id,
  ]

  admin_ssh_key {
    username   = "ubuntu"
    public_key = file(var.exp_pub_key)
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
    azurerm_linux_virtual_machine.azure-experiment-worker,
    azurerm_public_ip.azure-experiment-worker-public-ip
  ]
  # setup ssh connection for provisioners
  connection {
    user = "ubuntu"
    host = azurerm_linux_virtual_machine.azure-experiment-worker.public_ip_address
    type = "ssh"
    private_key = file(var.exp_pvt_key)
    timeout = "2m"
  }

  # copy local files to remote server
  # useage: https://www.terraform.io/docs/provisioners/file.html
  # provisioner "file" {
    # source = "../../benchmark"
    # destination = "/home/ubuntu"
  # }

  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      # "sudo apt update",
      # "sudo apt install -y git python3 python3-pip",
      # "git clone https://github.com/zanderhavgaard/thesis-code",
      # "python3 --version",
      "ls -al",
    ]
  }
}
