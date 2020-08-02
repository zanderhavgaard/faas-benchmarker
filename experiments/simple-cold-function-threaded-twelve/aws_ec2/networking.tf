# attach elastic public ip to instance
resource "aws_eip" "simple-cold-function-threaded-twelve1-worker-eip" {
  instance = aws_instance.simple-cold-function-threaded-twelve1-worker-aws.id
  vpc      = true
}
