# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================


from django.test import TestCase
import json
import sys
import os
from athena_app_cmdb import models

from mock import MagicMock

# Some tests use a static file 'virtuals_ucmdb_response_multiple_vcenterts.json'.
# See test_pull_virtuals_from_ucmdb.py for details about how to regenerate this file.

class PodsAcceptanceTests(TestCase):

    def setUp(self):
        # set up initial data for testing
        content_file = open(os.path.join(os.path.dirname(__file__), 'init_data.json'), 'r')
        content = json.loads(content_file.read())
        pods_data = content['pods']
        for pod in pods_data:
            models.pod.objects.create(**pod)

    # Tests listing all pods
    def test_list_return_empty_when_no_data(self):
        # Wipe all the data pods data before running test
        models.pod.objects.all().delete()

        response = self.client.get('/api/athena_app_cmdb/pods')

        self.assertEqual(response.status_code, 404)
        body = json.loads(response.content)

        self.assertEqual(body['detail'], "Not found.")
        # Confirmation
        print
        "Pods: " + sys._getframe().f_code.co_name + " - OK"

    def test_list_returns_200_when_entries_found(self):
        # Wipe all the data pods data before running test
        models.pod.objects.all().delete()

        # Simulates getting information
        content_file = open(os.path.join(os.path.dirname(__file__), 'multiple_pods_list_response.json'), 'r')
        mock_client = MagicMock()
        mock_client.execute_topology_query.return_value = json.loads(content_file.read())

        # Confirmation
        print
        "Pods: " + sys._getframe().f_code.co_name + " - OK"
