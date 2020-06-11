# register ssh keys with aws
resource "aws_key_pair" "faasbenchmarker-key" {
  key_name = "faasbenchmarker"
  public_key = file(var.client_pub_key)
}

# create VPC
resource "aws_vpc" "faasbenchmarker-vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
  tags = {
    Name = "faasbenchmarker-vpc"
  }
}

# create internet gateway to VPC
resource "aws_internet_gateway" "faasbenchmarker-vpc-gateway" {
  vpc_id = aws_vpc.faasbenchmarker-vpc.id
  tags = {
    Name = "faasbenchmarker-vpc-gateway"
  }
}

# create VPC subnet
resource "aws_subnet" "faasbenchmarker-subnet" {
  cidr_block = cidrsubnet(aws_vpc.faasbenchmarker-vpc.cidr_block, 3, 1)
  vpc_id = aws_vpc.faasbenchmarker-vpc.id
  availability_zone = "eu-west-1c"
}

# create routing table in subnet
resource "aws_route_table" "faasbenchmarker-vpc-route-table" {
  vpc_id = aws_vpc.faasbenchmarker-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.faasbenchmarker-vpc-gateway.id
  }
  tags = {
    Name = "faasbenchmarker-vpc-route-table"
  }
}
# attach route table to subnet
resource "aws_route_table_association" "subnet-association" {
  subnet_id      = aws_subnet.faasbenchmarker-subnet.id
  route_table_id = aws_route_table.faasbenchmarker-vpc-route-table.id
}

# setup security group to allow traffic from outside VPC
resource "aws_security_group" "allow-ssh" {
  name = "allow-ssh"
  vpc_id = aws_vpc.faasbenchmarker-vpc.id
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
