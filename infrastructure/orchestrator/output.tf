# output ip address
output "ip_address" {
  value = digitalocean_droplet.orchestrator.ipv4_address
}
