# attach elastic public ip to instance
resource "aws_eip" "function-lifetime1-worker-eip" {
  instance = aws_instance.function-lifetime1-worker-aws.id
  vpc      = true
}
