terraform {
  cloud {
  organization = "zphyrs"
    workspaces {
      tags = ["zs-workload-automation-demo"]
    }
  }
  required_providers {
    zia = {
      source = "zscaler/zia"
      version = "2.3.1"
    }
  }
}

provider "zia" {}
