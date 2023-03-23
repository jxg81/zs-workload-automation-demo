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
}

locals {
    # Change this domain name to match the domain used in your ZIA tenant which you would like the users created in
    domain = "zphyrs.com"
    apps_json_files = fileset(path.module, "./config/apps/*.json")   
    apps_data  = [ for f in local.apps_json_files : jsondecode(file("${path.module}/${f}")) ]
    users_data = csvdecode(file("./config/users.csv"))
}
# In this basic example the password for all users is set to the same value
# The value is taken from an environment variable setting in the terrafrom cloud workspace called "PASSWORD"
# In a real world deployment you would want to extract this data from a secure vault
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
  user = module.users[each.value.username].user_data
  locations = each.value.locations
  description = each.value.description

}

output "test" {
  value = module.users
  sensitive = true
}

output "test2" {
  value = module.users[erp_app].userdata
  sensitive = true
}