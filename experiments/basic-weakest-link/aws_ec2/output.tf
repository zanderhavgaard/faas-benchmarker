output "ip_address" {
  value = aws_eip.basic-weakest-link1-worker-eip.public_ip
}
