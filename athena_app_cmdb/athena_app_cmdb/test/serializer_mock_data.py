mockasset =  {
        "id": "svc-example-test",
        "cicd": "https://bamboo.cdk.com/browse/NGIP-SVCEXAMPLETEST",
        "name": "example-test",
        "repo": "https://stash.cdk.com/projects/EXAMPLE/repos/svc-example-test/browse",
        "team": "team-example-team",
        "type": "svc",
        "product": "example-product",
        "internal": [
        {
            "environment": "us-dev",
            "entries": False
        },
        {
            "environment": "us-stage",
            "entries": False
        },
        {
            "environment": "us-prod",
            "entries": False
        }
        ],
    "security": [
        {
            "environment": "us-dev",
            "entries": [
            {
                "provider": "none"
            }
            ]
        },
        {
            "environment": "us-stage",
            "entries": [
            {
                "provider": "none"
            }
            ]
        },
        {
            "environment": "us-prod",
            "entries": [
            {
                "provider": "none"
            }
            ]
        }
        ],
        "appLanguage": "python",
        "description": "example test",
        "assetMasterId": 500
    }

mockteam = {
    "id": "team-example-team",
    "name": "example-team",
    "deleted": False,
    "_type": "team",
    "email": [
        "example@cdk.com"
    ],
    "ad-group": [
        "Example Developers",
        "Example Developers (DSI)"
    ],
    "opsgenie": {
        "name": "example",
        "create": True,
        "manager": "example@cdk.com"
    },
    "description": "Example eam",
    "notification": [
        {
            "email": "Example@cdk.com"
        },
        {
            "slack": "https://cdk-global.slack.com/archives/example"
        }
    ]
}

mockproduct = {
    "id": "example-product",
    "deleted": False,
    "security": [
        {
            "provider": "fortellis",
            "configuration": {}
        }
    ],
    "external-ids": {
        "iqr_product_id": 1234
    },
    "bamboo-projects": [
        {
            "id": "EXAMPLE"
        }
    ],
    "bitbucket-projects": [
        {
            "id": "EXAMPLE"
        }
    ]
}

mockresource = {
    "spec": {
        "type": "aws-elasticache-redis",
        "owner": "team-example-team",
        "platform": "location-us-nonprod",
        "definition": {
            "props": {
                "family": "redis6.x",
                "engineVersion": "6.x",
                "authentication": [
                    "Example"
                ],
                "parameterGroup": {},
                "backupRetention": 0,
                "accessExternally": False
            },
            "version": "001",
            "templateName": "athena-redis-mini",
            "encryptionRest": False,
            "encryptionTransit": False
        },
        "provisioner": {
            "type": "terraform",
            "source": ""
        },
        "assetMasterId": 325
    },
    "metadata": {
        "name": "example-resource",
        "annotations": {
            "iqr_product_id": "7210"
        },
        "description": "Example Resource"
    },
    "kind": "Resource",
    "apiVersion": "cdk.com/v1"
}

mocklocation = {
    "id": "location-us-dev",
    "name": "us-dev",
    "env-type": "dev",
    "domain": "example-dev.connectcdk.com",
    "region": "us",
    "status": "live",
    "_type": "location",
    "clusters": {
      "primary": "example_cluster"
    },
    "parameters": {
      "integrations": {
        "aws": {
          "id": "711406216734",
          "name": "cdk-aws-example-dev",
          "partition": "aws",
          "account-type": "dev",
          "cf-acm-region": "us-east-1",
          "primary-region": "us-west-2",
          "secondary-region": "us-east-1"
        },
        "okta": {
          "url": "https://connectcdk-dev.oktapreview.com"
        },
        "dockerRegistries": [
          {
            "type": "artifactory",
            "default": True,
            "dockerEndpoint": "artifactory.cdk.com"
          }
        ]
      }
    },
    "description": "Example Development Platform (US)"
  }

mockassetenvironment = {
    "id": "example-asset-environment",
    "asset": "svc-example-test"

}

mockcluster = {
    "id": "example_cluster_id",
    "uri": "https://7354A20DD24328892CEBAFE85866321D.gr7.us-west-2.eks.amazonaws.com"
  }