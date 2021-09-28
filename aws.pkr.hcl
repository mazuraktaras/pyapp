packer {
  required_plugins {
    amazon = {
      version = ">= 0.0.2"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

source "amazon-ebs" "ubuntu" {
  ami_name      = "lll-linux-aws"
  instance_type = "t3.micro"
  region        = "eu-north-1"
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-bionic-18.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  ssh_username = "ubuntu"
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
#      "sleep 30",
#      "sudo apt-get update",
      "env"
#      "sudo apt-get install -y redis-server",
#      "echo \"FOO is $FOO\" > example.txt",
    ]
  }
}
