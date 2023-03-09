variable "PASSWORD" {
    type        = string
    description = "Password to ve used for all user creation"
}

data "zia_location_management" "home" {
  name = "Home"
}
data "zia_department_management" "workloads" {
  name = "workloads"

}
data "zia_group_management" "package_management" {
  name = "package_management"
}

data "zia_group_management" "security_services" {
  name = "security_services"
}

data "zia_user_management" "julian" {
  name = "Julian Greensmith"
}
resource "zia_user_management" "erp_app" {
  name         = "erp_app"
  email        = "erp_app@zphyrs.com"
  password     = var.PASSWORD
  groups {
    id = [data.zia_group_management.package_management.id, data.zia_group_management.security_services.id]
  }
  department {
    id = data.zia_department_management.workloads.id
  }
}

resource "zia_user_management" "web_app" {
  name         = "web_app"
  email        = "web_app@zphyrs.com"
  password     = var.PASSWORD
  groups {
    id = [data.zia_group_management.package_management.id, data.zia_group_management.security_services.id]
  }
  department {
    id = data.zia_department_management.workloads.id
  }
}

resource "zia_user_management" "payroll_app" {
  name         = "payroll_app"
  email        = "payroll_app@zphyrs.com"
  password     = var.PASSWORD
  groups {
    id = [data.zia_group_management.package_management.id, data.zia_group_management.security_services.id]
  }
  department {
    id = data.zia_department_management.workloads.id
  }
}