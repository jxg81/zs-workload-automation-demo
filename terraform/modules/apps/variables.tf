variable "name" {
    type        = string
    description = "Application Name"
}
variable "urls" {
    type        = set(string)
    description = "List of permitted URLs"
}

variable "username" {
    type        = string
    description = "Authentication username permitted for access to URL list"
}

variable "locations" {
    type        = set(string)
    description = "Locations permitted for access to URL list"
}

variable "description" {
    type        = string
    description = "Freeform description of application"
}