# attach elastic public ip to instance
resource "aws_eip" "changeme1-worker-eip" {
  instance = aws_instance.changeme1-worker-aws.id
  vpc      = true
}
