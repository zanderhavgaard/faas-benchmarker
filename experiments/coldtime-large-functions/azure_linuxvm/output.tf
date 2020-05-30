# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.coldtime-large-functions-worker.public_ip_address
}
