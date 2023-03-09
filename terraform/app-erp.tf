resource "zia_url_categories" "erp_allow_list" {
  super_category      = "USER_DEFINED"
  configured_name     = "erp_allow_list"
  custom_category     = true
  type                = "URL_CATEGORY"
  urls = [
    ".sap.com",
    ".salesforce.com",
    ".oracle.com"
  ]
}

resource "zia_url_filtering_rules" "app_erp_rule" {
    name                = "app_erp_rule"
    description         = "allow erp app destinations"
    state               = "ENABLED"
    action              = "ALLOW"
    locations {
      id = [data.zia_location_management.home.id]
    }
    order               = 1
    url_categories      = [resource.zia_url_categories.erp_allow_list.id]
    protocols           = ["ANY_RULE"]
    request_methods     = [ "CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "OTHER", "POST", "PUT", "TRACE"]
    users {
      id = [resource.zia_user_management.erp_app.id]
    }
}