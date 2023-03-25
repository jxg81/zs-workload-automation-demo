terraform {
  required_providers {
    zia = {
      source = "zscaler/zia"
    }
  }
}

resource "random_password" "user_password" {
  length  = 16
  special = true
  keepers = {
    user_name = var.name
  }
}

data "zia_group_management" "group" {
  for_each = var.groups
  name     = each.value
}

data "zia_department_management" "workloads" {
  name = "workloads"
}

resource "zia_user_management" "user" {
  name     = var.name
  email    = join("@", [var.name, var.domain])
  password = resource.random_password.user_password.result
  groups {
    id = [for item in data.zia_group_management.group : item.id]
  }
  department {
    id = data.zia_department_management.workloads.id
  }
}

resource "vault_kv_secret_v2" "vault_store_user_pass" {
  mount               = var.vault_store
  name                = var.name
  delete_all_versions = true
  data_json = jsonencode(
    {
      password = resource.zia_user_management.user.password,
    }
  )
  custom_metadata {
    data = {

      username = resource.zia_user_management.user.name,
      email    = resource.zia_user_management.user.email,
      id       = resource.zia_user_management.user.id
    }
  }
}
