data "zia_department_management" "workloads" {
  name = "workloads"

}
data "zia_group_management" "package_management" {
  name = "package_management"
}

data "zia_group_management" "security_services" {
  name = "security_services"
}

resource "zia_user_management" "erp_app" {
  name         = "erp_app"
  email        = "erp_app@zphyrs.com"
  password     = "P@ssw0rd123*"
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
  password     = "P@ssw0rd123*"
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
  password     = "P@ssw0rd123*"
  groups {
    id = [data.zia_group_management.package_management.id, data.zia_group_management.security_services.id]
  }
  department {
    id = data.zia_department_management.workloads.id
  }
}