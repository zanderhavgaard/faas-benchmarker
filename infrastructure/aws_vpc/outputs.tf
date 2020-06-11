
output "subnet_id" {
  value = aws_subnet.faasbenchmarker-subnet.id
}

output "securtity_group_id" {
  value = aws_security_group.allow-ssh.id
}
