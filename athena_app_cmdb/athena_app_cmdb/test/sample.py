from django.test import TestCase
from athena_app_cmdb import models

class LocationTestCase(TestCase):
    def setUp(self):
        models.Location.objects.create(location_id="us-west-2", sound="Oregon")

    def check_location_exist(self):
        location = models.Location.objects.get(location_id="us-west-2")
        self.assertEqual(location.name, "Oregon")