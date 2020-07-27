# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.simple-cold-function-openfaas-worker.public_ip_address
}
