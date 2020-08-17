output "ip_address" {
  value = aws_eip.coldstart-nested1-worker-eip.public_ip
}
