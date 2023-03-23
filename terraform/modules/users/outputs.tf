output "user_data" {
  value = toset([resource.zia_user_management.user.id,resource.zia_user_management.user.name])
}