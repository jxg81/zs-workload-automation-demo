variable "domain" {
  type        = string
  description = "Domain name used to create user ID"
}
variable "name" {
  type        = string
  description = "User Name"
}
variable "groups" {
  type        = set(string)
  description = "User group assignments"
}
variable "department" {
  type        = string
  description = "User department assignment"
}
variable "vault_store" {
  type        = string
  description = "Vault store name"
}
variable "password_control" {
  type        = string
  description = "Random string to manage password chnages"
}
variable "special" {
  type        = bool
  description = "Require special characters in password"
}