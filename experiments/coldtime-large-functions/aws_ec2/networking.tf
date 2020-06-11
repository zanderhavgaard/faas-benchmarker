# attach elastic public ip to instance
resource "aws_eip" "coldtime-large-functions1-worker-eip" {
  instance = aws_instance.coldtime-large-functions1-worker-aws.id
  vpc      = true
}
