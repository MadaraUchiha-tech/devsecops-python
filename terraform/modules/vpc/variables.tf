variable "name" {
  type = string
}

variable "cidr" {
  type = string
}

variable "azs" {
  description = "Availability zones; one public and one private subnet is created in each"
  type        = list(string)
}

variable "cluster_name" {
  description = "EKS cluster name, used for the subnet discovery tags"
  type        = string
}
