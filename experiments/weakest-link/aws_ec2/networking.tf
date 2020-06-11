# attach elastic public ip to instance
resource "aws_eip" "weakest-link1-worker-eip" {
  instance = aws_instance.weakest-link1-worker-aws.id
  vpc      = true
}
