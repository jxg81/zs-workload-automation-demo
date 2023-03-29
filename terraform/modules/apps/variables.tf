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
variable "source_ip_list" {
    type        = set(string)
    description = "List of valid source IPs"
}
variable "order" {
    type = number
    description = "The order of the rules"
}
  # The following variable is only here becuase user and apps run in one workflow and i need to ensure any user creation occurs prior to trying to read data back from vault
  # I was using depends_on but it was creating some odd issues
variable "user_id" {
    type = number
    description = "User id for user mapping"
}