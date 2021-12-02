# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================

from django.test import TestCase
from django.test.client import Client
from django.test import TestCase
from rest_framework.renderers import JSONRenderer
from athena_app_cmdb import serializers
from athena_app_cmdb.models import Team
from athena_app_cmdb.test.serializer_mock_data import mockteam
from django.utils.encoding import force_text
from unittest.mock import Mock
from athena_app_cmdb.models import Asset, Product, Team, AppLanguage, AssetType, AssetEnvironment, ProductEnvironment, Location, EnvType

MODELS = [Team]

class TeamViewTests(TestCase):
    '''This class tests the views for :class:`~app.models.SampleModel` objects.'''

    def setUp(self):
        """Instantiate the test client.  Creates a test user."""
        self.client = Client()
        Team.objects.create(refid="test-team-1", name="test-team-1", properties={"ad-group":["test group"]})
        Team.objects.create(refid="test-team-2", name="test-team-2", properties={"ad-group":["test group"]})

    def test_teams_list(self):
        """This tests the samplemodel-listview, ensuring that templates are loaded correctly.
        This view uses a user with superuser permissions so does not test the permission levels for this view."""

        response = self.client.get('/teams')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(force_text(response.content), '[{"id":"test-team-2","name":"test-team-2","deleted":false,"ad-group":["test group"]},{"id":"test-team-1","name":"test-team-1","deleted":false,"ad-group":["test group"]}]')

    def test_one_team_test(self):
        """This tests the samplemodel-listview, ensuring that templates are loaded correctly.
        This view uses a user with superuser permissions so does not test the permission levels for this view."""

        response = self.client.get('/teams/test-team-2')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(force_text(response.content), '{"id":"test-team-2","name":"test-team-2","deleted":false,"ad-group":["test group"]}')


class AssetUrlsItemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        appLang=AppLanguage.objects.create(id="java", name="java")
        envtype=EnvType.objects.create(id="test", name="test-env")
        location=Location.objects.create(refid="test-location", name="test-location", env_type=envtype, domain="test.com", properties = { "_type": "location", "clusters": { "primary": "athena_null_value" }, "parameters": { "integrations": { "aws": { "id": "758029684819", "name": "cdk-aws-athenaplatform-prod", "partition": "aws", "account-type": "prod", "cf-acm-region": "us-east-1", "primary-region": "eu-west-1", "secondary-region": "eu-west-2" }, "dockerRegistries": [ { "type": "artifactory", "dockerEndpoint": "artifactory.cobalt.com" } ] } }, "description": "Athena Production Platform (EU)" })
        product=Product.objects.create(refid="test-product", properties = { "security": [ { "provider": "none" } ], "external-ids": { "iqr_product_id": 1234 }, "bamboo-projects": [ { "id": "NGIP" } ], "bitbucket-projects": [ { "id": "ATHENAP" } ] })
        productenv = ProductEnvironment.objects.create(refid="test-product-env", product=product, location=location, type=envtype, prefix = "us-dev")
        team=Team.objects.create(refid="test-team", name="test team")
        type=AssetType.objects.create(name="svc")
        asset=Asset.objects.create(refid="svc-example-test", name="example-app", product=product, team=team, type=type, appLanguage=appLang, repo="http://test-repo")
        AssetEnvironment.objects.create(refid="test-asset-env", asset=asset, product_environment=productenv, properties={ "consumes": [ { "port": 80, "additionalUrls": [], "type": "external", "value": "*.connectcdk.com", "protocol": "http" } ], "security": [ { "provider": "adfs-sso" } ] })
    def test_get(self):
        response = self.client.get('/assets/svc-example-test/urls')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(force_text(response.content), '[{"environment_id":"test-product-env","type":"test","url":"https://us-dev-example-app.test.com","additionalUrls":[]}]')
