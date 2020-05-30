output "ip_address" {
  value = aws_eip.coldtime-large-functions1-worker-eip.public_ip
}
