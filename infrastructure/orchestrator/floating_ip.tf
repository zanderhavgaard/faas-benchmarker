resource "digitalocean_floating_ip" "static-orchestrator-ip" {
  region = "fra1"
  lifecycle {
    prevent_destroy = true
  }
}

resource "digitalocean_floating_ip_assignment" "public-ip" {
  ip_address = digitalocean_floating_ip.static-orchestrator-ip.ip_address
  droplet_id = digitalocean_droplet.orchestrator.id
}

output "static_ip" {
  value = digitalocean_floating_ip.static-orchestrator-ip.ip_address
}
