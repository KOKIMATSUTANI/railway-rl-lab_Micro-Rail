variable "instance_name" {
  description = "Value of the EC2 instance's Name tag."
  type        = string
  default     = "gross-experiment"
}

variable "instance_type" {
  description = "The EC2 instance's type."
  type        = string
  default     = "t2.micro"
}

variable "az_count" {
  type        = number
  default     = 2
  description = "Number of AZs to cover"
}

# The VPC ID to use for the security group. 
variable "project_name" {
  type        = string
  description = "Resource name prefix"
  default     = "gross-experiment"  #(when destroying VPC and security group)
}

variable "experiment_name" {
  type        = string
  description = "Experiment name"
  default     = "dresden"
}

/*
variable "vpc_id" {
  type        = string
  description = "VPC ID"
}
*/