# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

from django.test import TestCase
from athena_app_cmdb.models import Location

class LocationModelTests(TestCase):
    def setUp(self):
        Location.objects.create(refid="us-west-2", name="Oregon")

    def test_location_exist(self):
        location = Location.objects.get(refid="us-west-2")
        self.assertEqual(location.name, "Oregon")

    def test_string_representation(self):
        location = Location(refid="us-west-2", name="Oregon")
        self.assertEqual(str(location), location.refid)