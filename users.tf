data "zia_department_management" "workloads" {
  name = "workloads"

}
data "zia_group_management" "package_management" {
  name = "package_management"
}

data "zia_group_management" "partner_sites" {
  name = "partner_sites"
}

resource "zia_user_management" "john_ashcroft" {
  name         = "John Ashcroft"
  email        = "john.ashcroft@acme.com"
  password     = "P@ssw0rd123*"
  groups {
    id = [data.zia_group_management.package_management.id, data.zia_group_management.partner_sites.id]
  }
  department {
    id = data.zia_department_management.workloads.id
  }
}