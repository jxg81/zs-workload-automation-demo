terraform {
  required_providers {
    zia = {
      source  = "zscaler/zia"
    }
  }
}

data "vault_generic_secret" "user_data" {
  path = join("/", ["kv", var.username])
}

data "zia_location_management" "location" {
  for_each = var.locations
  name = each.value
}

data "zia_firewall_filtering_network_service" "http" {
  name = "HTTP"
}

data "zia_firewall_filtering_network_service" "https" {
  name = "HTTPS"
}

resource "zia_firewall_filtering_destination_groups" "dstn_domain_group" {
  name        = join("-", [var.name, "destination_wildcard_fqdn_list"])
  description = join(" ", ["Allowed wildcard fqdns for application", var.name])
  type        = "DSTN_DOMAIN"
  addresses = var.urls
}

resource "zia_firewall_filtering_rule" "firewall_rule" {
    name                = join("-", [var.name, "application policy"])
    description         = join(" ", ["Policy for application", var.name])
    action              = "ALLOW"
    state               = "ENABLED"
    enable_full_logging = true
    locations {
      id = [for item in data.zia_location_management.location : item.id]
    }
    dest_ip_groups {
      id = [resource.zia_firewall_filtering_destination_groups.dstn_domain_group.id]
    }
    nw_services {
        id = [data.zia_firewall_filtering_network_service.http.id, data.zia_firewall_filtering_network_service.https.id]
    }
    users {
        id = [var.user_id]
    }
}

output "data_id" {
  value = data.vault_generic_secret.user_data.data.id
}

output "data_password" {
  value = data.vault_generic_secret.user_data.data.password
}