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

locals {
    json_files = fileset(path.module, "./config/apps/*.json")   
    json_data  = [ for f in local.json_files : jsondecode(file("${path.module}/${f}")) ]
    
}

module "application" {
  for_each = { for f in local.json_data : f.name => f }
  source = "./modules/apps"
  name = each.value.name
  urls = each.value.urls
  username = each.value.username
  locations = each.value.locations
  description = each.value.description

}