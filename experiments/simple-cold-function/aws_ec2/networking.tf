# attach elastic public ip to instance
resource "aws_eip" "simple-cold-function1-worker-eip" {
  instance = aws_instance.simple-cold-function1-worker-aws.id
  vpc      = true
}
