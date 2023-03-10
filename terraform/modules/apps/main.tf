
terraform {
  required_providers {
    zia = {
      source = "zscaler/zia"
      version = "2.3.1"
    }
  }
}

data "zia_location_management" "location" {
  for_each = var.locations
  name = each.value
}

resource "zia_url_categories" "custom_cat" {
    super_category      = "USER_DEFINED"
    configured_name     = join("-", [var.name, "allow_list"])
    custom_category     = true
    type                = "URL_CATEGORY"
    urls                = var.urls
}

resource "zia_url_filtering_rules" "filtering_rule" {
    name                = join("-", [var.name, "rule"])
    description         = var.description
    state               = "ENABLED"
    action              = "ALLOW"
    order               = 1
    url_categories      = [zia_url_categories.custom_cat.id]
    protocols           = ["ANY_RULE"]
    request_methods     = [ "CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "OTHER", "POST", "PUT", "TRACE"]
    locations {
      id = [for item in data.zia_location_management.location : item.id]
    }
#    users {
#      id = [resource.zia_user_management.user.id]
#    }
}