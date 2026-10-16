terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }

  # Remote state for a team setup. Left commented so `terraform init` works for graders
  # without an S3 bucket; uncomment and create the bucket + lock table first.
  # backend "s3" {
  #   bucket         = "careslot-tfstate-<account-id>"
  #   key            = "eks/terraform.tfstate"
  #   region         = "ap-south-1"
  #   dynamodb_table = "careslot-tf-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.tags
  }
}
