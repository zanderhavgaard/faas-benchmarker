# attach elastic public ip to instance
resource "aws_eip" "linear-invocation1-worker-eip" {
  instance = aws_instance.linear-invocation1-worker-aws.id
  vpc      = true
}
