# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

from django.test import TestCase
from rest_framework.renderers import JSONRenderer
from athena_app_cmdb.models import Asset, Location, Team, Product, Resource, AssetType, AppLanguage
from athena_app_cmdb import serializers 
from athena_app_cmdb.test.serializer_mock_data import mockasset, mockteam, mockproduct


class TeamSerializerTest(TestCase):
#this tests taking serialized data (native python data type) and converting it to validated data that can be stored in a model
    def test_deserialization(self):
        #get the serializer class associated with teams
        serializer_class = serializers.serializer_class_lookup['teams']
        #create serializer with mock team data
        serializer = serializer_class(data=mockteam)
        #check to ensure the serializer is valid
        serializer.is_valid()
        #save the serializer, this returns the team model object that was created
        team = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(team.name, "example-team")
#test taking an existing model (we create it at the start of the function, reusing the functionality of the old test, and serialize it into python native datatypes)
    def test_serialization(self):
        #get the serializer class associated with teams
        serializer_class = serializers.serializer_class_lookup['teams']
        #create serializer with mock team data
        serializer = serializer_class(data=mockteam)
        #check to ensure the serializer is valid
        serializer.is_valid()
        #save the serializer, this returns the team model object that was created
        team = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(team.name, "example-team")
        #use the team serializer to serialize the created team model, then we can verify the data is in the form of a dictionary and correct
        serializer = serializers.TeamSerializer(team)
        dictionary = serializer.data
        self.assertEqual("example-team", dictionary['name'])

class ProductSerializerTest(TestCase):
    def test_deserialization(self):
        #get the serializer class associated with teams
        serializer_class = serializers.serializer_class_lookup['products']
        #create serializer with mock team data
        serializer = serializer_class(data=mockproduct)
        #check to ensure the serializer is valid
        serializer.is_valid()
        #save the serializer, this returns the team model object that was created
        product = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(product.name, "example-product")
    def test_serialization(self):
        print("here")









