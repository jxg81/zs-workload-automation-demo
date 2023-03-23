output "user_data" {
  value = toset([resource.zia_user_management.users.id,resource.zia_user_management.users.name])
}