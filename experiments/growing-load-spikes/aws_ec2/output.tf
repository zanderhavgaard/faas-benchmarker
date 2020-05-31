output "ip_address" {
  value = aws_eip.growing-load-spikes1-worker-eip.public_ip
}
