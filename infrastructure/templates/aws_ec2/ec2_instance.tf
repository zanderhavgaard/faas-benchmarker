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

  provisioner "file" {
    source = "../../../secrets/ssh_keys/experiment_servers"
    destination = "/home/ubuntu/.ssh/id_rsa"
  }

  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",
      "sudo apt-get update -q",
      "sudo apt-get install -y -qq git python3 python3-dev python3-pip",
      "{ echo -n 'export fbrd=/home/ubuntu/faas-benchmarker\n' ; echo -n 'export PYTHONPATH=$PYTHONPATH:/home/ubuntu/faas-benchmarker/benchmark\n' ; echo -n 'export DB_HOSTNAME=${var.db_server_static_ip}\n' ; cat .bashrc ; } > /home/ubuntu/.bashrc.new",
      "mv .bashrc.new .bashrc",
      "chmod 600 /home/ubuntu/.ssh/id_rsa",
      "git clone --quiet https://github.com/zanderhavgaard/faas-benchmarker /home/ubuntu/faas-benchmarker",
      "cd /home/ubuntu/faas-benchmarker",
      "pip3 install -q -r requirements.txt",
    ]
  }

  # copy local files to remote server
  # useage: https://www.terraform.io/docs/provisioners/file.html
  provisioner "file" {
    source = var.env_file
    destination = var.remote_env_file
  }
}
