output "ip_address" {
  value = aws_eip.coldstart-identifier-nested1-worker-eip.public_ip
}
