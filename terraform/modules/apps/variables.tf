variable "name" {
    type        = string
    description = "Application Name"
}

variable "urls" {
    type        = set(string)
    description = "List of permitted URLs"
}

variable "username" {
    type = string
    description = "Username for user mapping"
}

variable "locations" {
    type        = set(string)
    description = "Locations permitted for access to URL list"
}

variable "description" {
    type        = string
    description = "Freeform description of application"
}

variable "vault_store" {
    type        = string
    description = "Vault store name"
}