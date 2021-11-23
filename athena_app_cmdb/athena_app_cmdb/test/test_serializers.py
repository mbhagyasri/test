# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

from django.test import TestCase
from rest_framework.renderers import JSONRenderer
from athena_app_cmdb.models import Asset, Location, Team, Product, Resource, AssetType, AppLanguage, LocationStatus, LocationRegion
from athena_app_cmdb import serializers 
from athena_app_cmdb.test.serializer_mock_data import mockasset, mockteam, mockproduct, mockresource, mocklocation
import copy

#Deserialization tests: test taking serialized data (native python data type) and converting it to validated data that can be stored in a model
#Serialization tests: test taking an existing model (we create it at the start of the function, reusing the functionality of the previous test, and serialize it into python native datatypes)

class TeamSerializerTest(TestCase):
    def test_deserialization(self):
        #get the serializer class associated with teams, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['teams']
        serializer = serializer_class(data=mockteam)
        serializer.is_valid()
        #save the serializer, this returns the team model object that was created
        team = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(team.name, "example-team")
    def test_serialization(self):
        #get the serializer class associated with teams, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['teams']
        serializer = serializer_class(data=mockteam)
        serializer.is_valid()
        team = serializer.save()
        self.assertEqual(team.name, "example-team")
        #use the team serializer to serialize the created team model, then we can verify the data is in the form of a dictionary and correct
        serializer = serializers.TeamSerializer(team)
        dictionary = serializer.data
        self.assertEqual("example-team", dictionary['name'])

class ProductSerializerTest(TestCase):
    def test_deserialization(self):
        #get the serializer class associated with products, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['products']
        data = copy.deepcopy(mockproduct)
        serializer = serializer_class(data=data)
        serializer.is_valid()
        #save the serializer, this returns the product model object that was created
        product = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(product.refid, "example-product")
    def test_serialization(self):
        #get the serializer class associated with products, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['products']
        serializer = serializer_class(data=mockproduct)
        serializer.is_valid()
        product = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(product.refid, "example-product")
        #use the team serializer to serialize the created product model, then we can verify the data is in the form of a dictionary and correct
        serializer = serializers.ProductSerializer(product)
        dictionary = serializer.data
        self.assertEqual("example-product", dictionary['id'])

class ResourceSerializerTest(TestCase):
    def test_deserialization(self):
        #get the serializer class associated with resources, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['resources']
        data = copy.deepcopy(mockresource)
        serializer = serializer_class(data=data)
        serializer.is_valid()
        #save the serializer, this returns the resource model object that was created
        resource = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual("example-resource", resource.refid)
    def test_serialization(self):
        #get the serializer class associated with resources, create serializer with mock data and check validity
        data = copy.deepcopy(mockresource)
        serializer_class = serializers.serializer_class_lookup['resources']
        serializer = serializer_class(data=data)
        print(serializer)
        serializer.is_valid()
        #save the serializer, this returns the resource model object that was created
        resource = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual("example-resource", resource.refid)
        serializer = serializers.ResourceSerializer(resource)
        dictionary = serializer.data
        self.assertEqual("example-resource", dictionary['metadata']['name'])

class LocationSerializerTest(TestCase):
    def test_deserialization(self):
        #get the serializer class associated with resources, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['locations']
        data = copy.deepcopy(mocklocation)
        serializer = serializer_class(data=data)
        #create associated model objects (referenced in mocklocation data)
        LocationStatus.objects.create(id="live", name="live")
        LocationRegion.objects.create(id="us", name="us")
        serializer.is_valid()
        #save the serializer, this returns the location model object that was created
        location = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(location.name, "us-dev")
    def test_serialization(self):
        #get the serializer class associated with locations, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['locations']
        data = copy.deepcopy(mocklocation)
        serializer = serializer_class(data=data)
        # create associated model objects (referenced in mocklocation data)
        LocationStatus.objects.create(id="live", name="live")
        LocationRegion.objects.create(id="us", name="us")
        serializer.is_valid()
        #save the serializer, this returns the location model object that was created
        location = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(location.name, "us-dev")
        serializer = serializers.LocationSerializer(location)
        dictionary = serializer.data
        self.assertEqual("location-us-dev", dictionary['id'])
