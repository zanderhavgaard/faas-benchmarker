# print ip address
output "ip_address" {
  value = aws_eip.changeme1-worker-eip.public_ip
}
