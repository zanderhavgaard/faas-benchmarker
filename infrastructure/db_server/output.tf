# output ip address
output "ip_address" {
  value = digitalocean_droplet.db-server.ipv4_address
}
