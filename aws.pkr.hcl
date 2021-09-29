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
  default = ""
}

source "amazon-ebs" "ubuntu" {

  ami_name      = "pyapp-linux-aws"
  instance_type = "t3.micro"
  region        = "eu-north-1"
  iam_instance_profile = "EC2_S3Role"
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
  ssh_pty = true
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
      "sudo apt-get install awscli unzip virtualenv -y",
#      "curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'",
#      "unzip awscliv2.zip",
#      "sudo ./aws/install",
##      "aws s3 ls",
#      "/usr/local/bin/aws --version",
#      "/usr/local/bin/aws s3 cp s3://${var.package} ./package.zip",
#      "unzip -o package.zip",
      "ls -alh",
      "env",
      "exit 1"
      #      "sudo apt-get install -y redis-server",
      #      "echo \"FOO is $FOO\" > example.txt",
    ]
  }
}
