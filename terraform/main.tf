terraform {
# Uncomment this backend config and update variables to store state files in remote location
#    backend "s3" {
#    bucket = "mybucket"
#    key    = "path/to/my/key"
#    region = "us-east-1"
# }
  cloud {
  # Set this value to match your terrafrom cloud organisation name
  organization = "zphyrs"
    workspaces {
      # Set this value to select the correct workspace in your terrafrom cloud organisation
      tags = ["zs-workload-automation-demo"]
    }
  }
  required_providers {
    zia = {
      version = "2.4.6"
      source  = "zscaler/zia"
    }
    vault = {
      source = "hashicorp/vault"
      version = "3.14.0"
    }
  }
}

provider "vault" {
  skip_tls_verify = true
}
locals {
    # Change this domain name to match the domain used in your ZIA tenant which you would like the users created in
    domain = "zphyrs.com"
    apps_json_files = fileset(path.module, "./config/apps/*.json")   
    apps_data  = [ for f in local.apps_json_files : jsondecode(file("${path.module}/${f}")) ]
    users_data = csvdecode(file("./config/users.csv"))
}

module "users" {
  for_each = { for f in local.users_data : f.name => f }
  source = "./modules/users"
  name = each.value.name
  groups = toset(split(":", each.value.groups))
  domain = local.domain
}
module "application" {
  for_each = { for f in local.apps_data : f.name => f }
  source = "./modules/apps"
  name = each.value.name
  urls = each.value.urls
  username = each.value.username
  user_id = module.users[each.value.username].user_data["user_id"]
  locations = each.value.locations
  description = each.value.description
}
output "test" {
  value = module.application
  sensitive = true
}
