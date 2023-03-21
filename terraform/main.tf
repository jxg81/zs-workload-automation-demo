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
    domain = "zphyrs.com"
    apps_json_files = fileset(path.module, "./config/apps/*.json")   
    apps_data  = [ for f in local.apps_json_files : jsondecode(file("${path.module}/${f}")) ]
    users_data = csvdecode(file("./config/users.csv"))
}
variable "PASSWORD" {
    type        = string
    description = "Password to ve used for all user creation"
}

module "users" {
  for_each = { for f in local.users_data : f.name => f }
  source = "./modules/users"
  name = each.value.name
  groups = toset(split(":", each.value.groups))
  password = var.PASSWORD
  domain = local.domain
}
module "application" {
  for_each = { for f in local.apps_data : f.name => f }
  source = "./modules/apps"
  name = each.value.name
  urls = each.value.urls
  username = each.value.username
  locations = each.value.locations
  description = each.value.description
}