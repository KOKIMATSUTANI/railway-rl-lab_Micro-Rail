provider "aws" {
  region = "eu-central-1"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"] # Canonical
}
data "aws_availability_zones" "available" {
  state = "available"
}

/* (for destroy VPC and security group ) 
resource "aws_security_group" "gross" {
  name        = "${var.project_name}-sg"
  description = "Security group for GROSS experiment"
  
  # The VPC ID to use existing security group. 
  # vpc_id      = var.vpc_id


  tags = {
    Name = "${var.project_name}-sg"
  }
}

# Allow outbound traffic so Docker and the CloudWatch Agent can access AWS APIs
# an d package repositories.
resource "aws_vpc_security_group_egress_rule" "gross_ipv4" {
  security_group_id = aws_security_group.gross.id
  description       = "Allow outbound IPv4 traffic"

  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
}



module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.19.0"

  name = "${var.project_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, var.az_count)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24"]

  enable_dns_hostnames    = true
  enable_dns_support      = true
}
# (for destroy VPC and security group )*/

/* (for destroy EC2 instance)
resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  
  # /* (for destroy VPC)
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  subnet_id              = module.vpc.public_subnets[0]
  # (for destroy VPC)  */

/* (for destroy EC2 instance) 
  root_block_device {
    volume_size           = 30       # Storage (GiB)
    volume_type           = "gp3"    # Volume type (gp3, io1, io2, sc1, st1, standard)
    iops                  = 3000     # IOPS baseline for gp3 (3,000 IOPS per volume)
    throughput            = 125      # Throughput baseline for gp3 (125 MiB/s)
    encrypted             = true     # Encryption
    delete_on_termination = true     # Delete EBS on instance termination

    tags = {
      Name = "app-server-root-ebs"
    }
  }

  tags = {
    Name = var.instance_name
  }
}
# (for destroy EC2 instance) */

