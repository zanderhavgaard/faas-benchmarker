# attach elastic public ip to instance
resource "aws_eip" "single-function-time-to-cold-start1-worker-eip" {
  instance = aws_instance.single-function-time-to-cold-start1-worker-aws.id
  vpc      = true
}
