terraform {
    required_providers {
        aws = {
        source  = "hashicorp/aws"
        version = "~> 4.0"
        }
    }
}

provider "aws" {
    region = "ap-southeast-1"
    profile = var.aws_profile
    shared_credentials_files = [pathexpand("~/.aws/credentials")]
}