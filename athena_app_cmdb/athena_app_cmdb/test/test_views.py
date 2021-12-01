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
