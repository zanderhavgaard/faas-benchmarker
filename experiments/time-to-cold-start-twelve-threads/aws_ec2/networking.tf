# attach elastic public ip to instance
resource "aws_eip" "time-to-cold-start-twelve-threads1-worker-eip" {
  instance = aws_instance.time-to-cold-start-twelve-threads1-worker-aws.id
  vpc      = true
}
