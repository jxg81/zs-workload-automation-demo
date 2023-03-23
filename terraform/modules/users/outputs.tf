output "user_data" {
  value = toset([zia_user_management.users.id,zia_user_management.users.name])
}