# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.coldtime-large-functions-openfaas-worker.public_ip_address
}
