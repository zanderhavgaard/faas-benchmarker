output "ip_address" {
  value = aws_eip.weakest-link1-worker-eip.public_ip
}
