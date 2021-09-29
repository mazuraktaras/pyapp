packer {
  required_plugins {
    amazon = {
      version = ">= 0.0.2"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "package" {
  type    = string
  default = "Hi"
}

source "amazon-ebs" "ubuntu" {
  assume_role {
    role_arn     = "arn:aws:iam::188178296807:role/EC2_S3Role"
#    session_name = "SESSION_NAME"
#    external_id  = "EXTERNAL_ID"
  }
  ami_name      = "pyapp-linux-aws"
  instance_type = "t3.micro"
  region        = "eu-north-1"
  source_ami_filter {
    filters     = {
      name                = "ubuntu/images/*ubuntu-bionic-18.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  ssh_username  = "ubuntu"
}

build {
  name    = "aws-packer"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]
  provisioner "shell" {
    #    environment_vars = [
    #      "FOO=hello world",
    #    ]
    inline = [
      "echo Installing Labels",
      "echo ${var.package}",
      #      "sleep 30",
      "sudo apt-get update -y",
      #      "sudo apt-get upgrade -y",
      #      "sudo apt install awscli -y",
      "sudo apt-get install unzip -y",
      "curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'",
      "unzip awscliv2.zip",
      "sudo ./aws/install",
      "aws s3 ls",
      "env",
      "exit 1"
      #      "sudo apt-get install -y redis-server",
      #      "echo \"FOO is $FOO\" > example.txt",
    ]
  }
}
