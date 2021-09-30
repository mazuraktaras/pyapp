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

locals {
  timestamp = replace(timestamp(), ":", "-")
}


source "amazon-ebs" "ubuntu" {

  ami_name             = "pyapp-ubuntu-${local.timestamp}"
  instance_type        = "t3.micro"
  region               = "eu-north-1"
  iam_instance_profile = "EC2_S3Role"
  source_ami_filter {
    filters = {
      #      name                = "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20210720"
      name                = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210430"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    #    most_recent = true
    owners  = ["099720109477"]
  }
  ssh_username         = "ubuntu"
  ssh_pty              = true
}

build {
  name    = "aws-packer"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]
  provisioner "shell" {

    inline = [
      "echo Installing Labels",
      "echo ${var.package}",
      #      "sleep 30",
      "sudo apt update",
      #      "sleep 5",
      #            "sudo apt-get upgrade -y",
      #      "sudo apt install awscli -y",
      "sudo apt install unzip",
      #      "sudo apt-get install awscli -y",
      #      "aws s3 cp ${var.package} ./package.zip",
      #      "unzip -o package.zip",
      #      "ls -alh",
      #      "sudo dpkg -i blog.deb",
      #      "env",
      #      "exit 1"
      #      "sudo apt-get install -y redis-server",
      #      "echo \"FOO is $FOO\" > example.txt",
    ]
  }
}
