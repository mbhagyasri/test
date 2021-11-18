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
