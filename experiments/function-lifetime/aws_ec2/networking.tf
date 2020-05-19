# register ssh keys with aws
resource "aws_key_pair" "function-lifetime1_worker_key" {
  key_name = "function-lifetime1_worker"
  public_key = file(var.client_pub_key)
}

# create VPC
resource "aws_vpc" "function-lifetime1-worker-vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
  tags = {
    Name = "function-lifetime1-worker-vpc"
  }
}

# attach elastic public ip to instance
resource "aws_eip" "function-lifetime1-worker-eip" {
  instance = aws_instance.function-lifetime1-worker-aws.id
  vpc      = true
}

# create internet gateway to VPC
resource "aws_internet_gateway" "function-lifetime1-worker-vpc-gateway" {
  vpc_id = aws_vpc.function-lifetime1-worker-vpc.id
  tags = {
    Name = "function-lifetime1-worker-vpc-gateway"
  }
}

# create VPC subnet
resource "aws_subnet" "function-lifetime1-worker-subnet" {
  cidr_block = cidrsubnet(aws_vpc.function-lifetime1-worker-vpc.cidr_block, 3, 1)
  vpc_id = aws_vpc.function-lifetime1-worker-vpc.id
  availability_zone = "eu-west-1c"
}

# create routing table in subnet
resource "aws_route_table" "function-lifetime1-worker-vpc-route-table" {
  vpc_id = aws_vpc.function-lifetime1-worker-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.function-lifetime1-worker-vpc-gateway.id
  }
  tags = {
    Name = "function-lifetime1-worker-vpc-route-table"
  }
}
# attach route table to subnet
resource "aws_route_table_association" "subnet-association" {
  subnet_id      = aws_subnet.function-lifetime1-worker-subnet.id
  route_table_id = aws_route_table.function-lifetime1-worker-vpc-route-table.id
}

# setup security group to allow traffic from outside VPC
resource "aws_security_group" "allow-ssh" {
  name = "allow-ssh"
  vpc_id = aws_vpc.function-lifetime1-worker-vpc.id
  ingress {
    cidr_blocks = [
      "0.0.0.0/0"
    ]
    from_port = 22
    to_port = 22
    protocol = "tcp"
  }
  # Terraform removes the default rule
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
