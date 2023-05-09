#Test
terraform {
  cloud {
    # Set this value to match your terrafrom cloud organisation name
    organization = "zphyrs"
    workspaces {
      # Set this value to select the correct workspace in your terrafrom cloud organisation
      tags = ["workload-users"]
    }
  }
  required_providers {
    zia = {
      version = "2.5.1"
      source  = "zscaler/zia"
    }
    vault = {
      source  = "hashicorp/vault"
      version = "3.14.0"
    }
  }
}

provider "vault" {
  # Vault token and address taken from env variables
  skip_tls_verify = true
}
locals {
  # Change this domain name to match the domain used in your ZIA tenant which you would like the users created in
  domain = "zphyrs.com"
  # Change this to macth the name of your vault store
  vault_store = "kv"
  users_data  = csvdecode(file("./config/users.csv"))
}

module "users" {
  for_each         = { for f in local.users_data : f.name => f }
  source           = "./modules/users"
  name             = each.value.name
  password_control = each.value.password_control
  groups           = toset(split(":", each.value.groups))
  department       = each.value.department
  domain           = local.domain
  vault_store      = local.vault_store
}
