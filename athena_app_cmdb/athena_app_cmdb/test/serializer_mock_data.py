mockasset =  {
        "id": "svc-example-test",
        "cicd": "https://bamboo.cdk.com/browse/NGIP-SVCEXAMPLETEST",
        "name": "example-test",
        "repo": "https://stash.cdk.com/projects/ATHENAP/repos/svc-example-test/browse",
        "team": "team-athena-platform",
        "type": "svc",
        "product": "athena",
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
        "AthenaPlatformDevelopers@cdk.com"
    ],
    "ad-group": [
        "Athena Platform Developers",
        "Athena Platform Developers (DSI)"
    ],
    "opsgenie": {
        "name": "athena-platform",
        "create": True,
        "manager": "athenaplatformdevelopers@cdk.com"
    },
    "description": "Athena Platform Team",
    "notification": [
        {
            "email": "AthenaPlatformDevelopers@cdk.com"
        },
        {
            "slack": "https://cdk-global.slack.com/archives/GPCG44ZPU"
        }
    ]
}

mockproduct = {
    "id": "example-product",
    "environments": [
        {
            "id": "us-dev",
            "type": "dev",
            "prefix": "dev",
            "location": "location-us-dev"
        },
        {
            "id": "us-prod",
            "type": "prod",
            "location": "location-us-prod"
        },
        {
            "id": "us-stage",
            "type": "stage",
            "prefix": "stage",
            "location": "location-us-nonprod"
        }
    ],
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
            "id": "NGIP"
        }
    ],
    "bitbucket-projects": [
        {
            "id": "ATHENAP"
        }
    ]
}