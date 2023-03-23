terraform {
  required_providers {
    zia = {
      version = "2.4.6"
      source  = "zscaler/zia"
    }
  }
}

data "zia_group_management" "group" {
  for_each = var.groups
  name = each.value
}

data "zia_department_management" "workloads" {
  name = "workloads"
}

resource "zia_user_management" "user" {
  name         = var.name
  email        = join("@", [var.name, var.domain])
  password     = var.password
  groups {
    id = [for item in data.zia_group_management.group : item.id]
  }
  department {
    id = data.zia_department_management.workloads.id
  }
}