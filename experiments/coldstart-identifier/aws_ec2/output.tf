output "ip_address" {
  value = aws_eip.coldstart-identifier1-worker-eip.public_ip
}
