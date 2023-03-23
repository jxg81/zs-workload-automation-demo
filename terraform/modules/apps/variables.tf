variable "name" {
    type        = string
    description = "Application Name"
}

variable "urls" {
    type        = set(string)
    description = "List of permitted URLs"
}

variable "user_id" {
    type = number
    description = "User id for user mapping"
}

variable "locations" {
    type        = set(string)
    description = "Locations permitted for access to URL list"
}

variable "description" {
    type        = string
    description = "Freeform description of application"
}

