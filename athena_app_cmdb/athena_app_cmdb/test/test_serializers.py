# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

from django.test import TestCase

from athena_app_cmdb.models import Location, Team, Product, Resource
from athena_app_cmdb import serializers 
from athena_app_cmdb.test.serializer_mock_data import mockasset

#test for asset serializer
class AssetSerializerTest(TestCase):
    #this case below occurs when a user creates an asset using the API e.g. POST request to /assets
    def test_create(self):
        #look up the serializer class for assets
        serializer_class = serializers.serializer_class_lookup['assets']
        #create serializer with data
        serializer = serializer_class(data=mockasset)
        #validate and save serializer
        if serializer.is_valid():
            serializer.save()
        #extract content from serializer
        content = serializer.data
        #assert that the cicd url is still the same as our mock_data used to create the asset, and that it now falls under 'properties'
        print(content['properties']['cicd'])
        self.assertEqual("https://bamboo.cdk.com/browse/NGIP-SVCEXAMPLETEST", content['properties']['cicd'])






