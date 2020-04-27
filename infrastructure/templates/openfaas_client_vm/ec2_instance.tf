# this terraform file creates an EC2 instance on aws

# ec2 instance
resource "aws_instance" "changeme1-worker-aws" {
  tags = {
    Name = "changeme1-worker"
  }
  ami = "ami-0701e7be9b2a77600"
  instance_type = "t2.micro"
  key_name = "changeme1_worker"
  subnet_id = aws_subnet.changeme1-worker-subnet.id
  security_groups = [aws_security_group.allow-ssh.id]
}

# HACK to run provisioners over SSH after instance
# has been created and recieved a public ip address
resource "null_resource" "ec2-provisioners" {
  # run the provisioners after the instance has been created
  # and the ip address has been assigned
  depends_on = [
    aws_eip.changeme1-worker-eip,
    aws_instance.changeme1-worker-aws
  ]
  # setup ssh connection for provisioners
  connection {
    user = "ubuntu"
    # host = aws_instance.experiment-worker-aws.public_ip
    host = aws_eip.changeme1-worker-eip.public_ip
    type = "ssh"
    private_key = file(var.client_pvt_key)
    timeout = "2m"
  }

  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      # wait for cloud-init to finish
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",
      # set some environment variables
      "{ echo -n 'export fbrd=/home/ubuntu/faas-benchmarker\n' ; echo -n 'export PYTHONPATH=$PYTHONPATH:/home/ubuntu/faas-benchmarker/benchmark\n' ; cat .bashrc ; } > /home/ubuntu/.bashrc.new",
      "mv .bashrc.new .bashrc",
      # update and install python
      "sudo apt-get update -q",
      "sudo apt-get install -y -qq unzip git python3 python3-dev python3-pip",
      # clone repo
      "git clone --quiet https://github.com/zanderhavgaard/faas-benchmarker /home/ubuntu/faas-benchmarker",
      # install python dependencies
      "cd /home/ubuntu/faas-benchmarker",
      "pip3 install -q -r requirements.txt",
      # install depenencies for creating the openfaas cluster
      "bash /home/ubuntu/faas-benchmarker/eks_openfaas_orchestration/install_openfaas_orchestration_tools.sh",
      # create directory for aws credentials
      "mkdir /home/ubuntu/.aws",
    ]
  }

  # copy AWS credentials to enable creating the EKS cluster for OpenFaas
  provisioner "file" {
    source = "../../../secrets/openfaas_orchestration_credentials/"
    destination = "/home/ubuntu/.aws"
  }
}
