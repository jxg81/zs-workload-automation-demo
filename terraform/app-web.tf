resource "zia_url_categories" "web_allow_list" {
  super_category      = "USER_DEFINED"
  configured_name     = "web_allow_list"
  custom_category     = true
  type                = "URL_CATEGORY"
  urls = [
    ".facebook.com",
    ".twitter.com"
  ]
}

resource "zia_url_filtering_rules" "web_erp_rule" {
    name                = "app_web_rule"
    description         = "allow web app destinations"
    state               = "ENABLED"
    action              = "ALLOW"
    order               = 1
    url_categories      = [resource.zia_url_categories.web_allow_list.id]
    protocols           = ["ANY_RULE"]
    request_methods     = [ "CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "OTHER", "POST", "PUT", "TRACE"]
    users {
      id = [resource.zia_user_management.web_app.id]
    }
}