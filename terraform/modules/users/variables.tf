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
variable "vault_store" {
    type        = string
    description = "Vault store name"
}