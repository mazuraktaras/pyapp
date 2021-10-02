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

  ami_name             = "pyapp-ubuntu ${local.timestamp}"
  instance_type        = "t3.micro"
  region               = "eu-north-1"
  iam_instance_profile = "EC2_Role"
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20210720"
      #      name                = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210430"
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
      "echo Preparing Initial Installation",
      "echo ${var.package}",
      "while [ ! -f  /var/lib/cloud/instance/boot-finished ]; do sleep 2; echo 'Waiting for cloud-init..'; done",
#      "sudo apt-get update -y",
#      #      "sudo apt-get upgrade -y",
#
#      "sudo apt-get install -y unzip",
#      "sudo apt-get install -y awscli",
#      "sudo apt-get install -y virtualenv",
#      "aws s3 cp ${var.package} ./package.zip",
#
#      "unzip -o package.zip",
#      "ls -alh",
#      #      "sudo dpkg -i blog.deb",
      "exit 1"
    ]
  }
  post-processor "manifest" {
#    output      = "manifest.json"
#    strip_path  = true
#    custom_data = {
#      my_custom_data = "example"
#    }
  }

}