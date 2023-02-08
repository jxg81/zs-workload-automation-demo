terraform {
# Uncomment this backend config and update variables to store state files in remote location
#    backend "s3" {
#    bucket = "mybucket"
#    key    = "path/to/my/key"
#    region = "us-east-1"
# }
  cloud {
  organization = "zphyrs"
    workspaces {
      tags = ["zs-workload-automation-demo"]
    }
  }
  required_providers {
    zia = {
      source = "zscaler/zia"
      version = "2.3.1"
    }
  }
}

provider "zia" {}