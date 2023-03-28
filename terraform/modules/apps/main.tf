terraform {
  required_providers {
    zia = {
      source = "zscaler/zia"
    }
  }
}

data "vault_kv_secret_v2" "user_data" {
  mount = var.vault_store
  name  = var.username
}

data "zia_location_management" "location" {
  for_each = var.locations
  name     = each.value
}

data "zia_firewall_filtering_network_service" "http" {
  name = "HTTP"
}

data "zia_firewall_filtering_network_service" "https" {
  name = "HTTPS"
}

resource "zia_firewall_filtering_rule" "firewall_rule" {
  name                = join("-", [var.name, "application policy"])
  description         = join(" ", ["Policy for application", var.name])
  order               = var.order
  action              = "ALLOW"
  state               = "ENABLED"
  enable_full_logging = true
  dest_addresses      = var.urls
  locations {
    id = [for item in data.zia_location_management.location : item.id]
  }
  nw_services {
    id = [data.zia_firewall_filtering_network_service.http.id, data.zia_firewall_filtering_network_service.https.id]
  }
  users {
    id = [tonumber(data.vault_kv_secret_v2.user_data.custom_metadata.id)]
  }
  lifecycle {
    precondition { 
      condition     = var.username != "" && var.source_ip_list != []
      error_message = "Must provide either username, or source ip list or both"
    }
  }
}
