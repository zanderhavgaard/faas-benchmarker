# output ip address
output "ip_address" {
  value = azurerm_linux_virtual_machine.concurrency-benchmarking-openfaas-worker.public_ip_address
}
