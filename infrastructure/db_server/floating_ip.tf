resource "digitalocean_floating_ip" "static-db-server-ip" {
  region = "fra1"
  lifecycle {
    prevent_destroy = true
  }
}

resource "digitalocean_floating_ip_assignment" "public-ip" {
  ip_address = digitalocean_floating_ip.static-db-server-ip.ip_address
  droplet_id = digitalocean_droplet.db-server.id
}

output "static_ip" {
  value = digitalocean_floating_ip.static-db-server-ip.ip_address
}
