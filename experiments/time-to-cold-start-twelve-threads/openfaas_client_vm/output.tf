# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.time-to-cold-start-twelve-threads-openfaas-worker.public_ip_address
}
