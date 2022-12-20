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
  email        = "erp_app@workloads.local"
  password     = "P@ssw0rd123*"
  groups {
    id = [data.zia_group_management.package_management.id, data.zia_group_management.security_services.id]
  }
  department {
    id = data.zia_department_management.workloads.id
  }
}