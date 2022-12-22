resource "zia_url_categories" "payroll_allow_list" {
  super_category      = "USER_DEFINED"
  configured_name     = "payroll_allow_list"
  custom_category     = true
  type                = "URL_CATEGORY"
  urls = [
    ".adp.com",
    ".xero.com"
  ]
}

resource "zia_url_filtering_rules" "app_payroll_rule" {
    name                = "app_payroll_rule"
    description         = "allow payroll app destinations"
    state               = "ENABLED"
    action              = "ALLOW"
    order               = 1
    url_categories      = [resource.zia_url_categories.payroll_allow_list.id]
    protocols           = ["ANY_RULE"]
    request_methods     = [ "CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "OTHER", "POST", "PUT", "TRACE"]
    users {
      id = [resource.zia_user_management.payroll_app.id]
    }
}