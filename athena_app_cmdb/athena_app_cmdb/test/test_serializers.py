# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

from django.test import TestCase
from rest_framework.renderers import JSONRenderer
from athena_app_cmdb.models import Asset, Location, Team, Product, Resource, AssetType, AppLanguage, LocationStatus, LocationRegion, AssetEnvironment, ProductEnvironment, Location, EnvType, Cluster
from athena_app_cmdb import serializers 
from athena_app_cmdb.test.serializer_mock_data import mockasset, mockteam, mockproduct, mockresource, mocklocation, mockassetenvironment, mockcluster
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
        #use the product serializer to serialize the created product model, then we can verify the data is in the form of a dictionary and correct
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
        serializer.is_valid()
        #save the serializer, this returns the resource model object that was created
        resource = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual("example-resource", resource.refid)
        serializer = serializers.ResourceSerializer(resource)
        dictionary = serializer.data
        self.assertEqual("example-resource", dictionary['metadata']['name'])

class LocationSerializerTest(TestCase):
    def setUp(self):
        #create associated model objects (referenced in mocklocation data)
        LocationStatus.objects.create(id="live", name="live")
        LocationRegion.objects.create(id="us", name="us")
    def test_deserialization(self):
        #get the serializer class associated with locations, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['locations']
        data = copy.deepcopy(mocklocation)
        serializer = serializer_class(data=data)
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
        serializer.is_valid()
        #save the serializer, this returns the location model object that was created
        location = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(location.name, "us-dev")
        serializer = serializers.LocationSerializer(location)
        dictionary = serializer.data
        self.assertEqual("location-us-dev", dictionary['id'])


class AssetSerializerTest(TestCase):
    def setUp(self):
        #create associated model objects (referenced in mockasset data)
        Product.objects.create(refid="example-product", properties={"example": "test"})
        Team.objects.create(refid="team-example-team")
        AssetType.objects.create(id="svc", name="svc")
        AppLanguage.objects.create(id="python", name="python")
    def test_deserialization(self):
        #get the serializer class associated with assets, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['assets']
        data = copy.deepcopy(mockasset)
        serializer = serializer_class(data=data)
        serializer.is_valid()
        #save the serializer, this returns the asset model object that was created
        asset = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(asset.refid, "svc-example-test")
    def test_serialization(self):
        #get the serializer class associated with assets, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['assets']
        data = copy.deepcopy(mockasset)
        serializer = serializer_class(data=data)
        serializer.is_valid()
        #save the serializer, this returns the asset model object that was created
        asset = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(asset.refid, "svc-example-test")
        #use asset serializer and check validity of returned serialized data
        serializer = serializers.AssetSerializer(asset)
        dictionary = serializer.data
        self.assertEqual("svc-example-test", dictionary['id'])

class ClusterSerializerTest(TestCase):
    def test_deserialization(self):
        #get the serializer class associated with clusters, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['clusters']
        data = copy.deepcopy(mockcluster)
        serializer = serializer_class(data=data)
        serializer.is_valid()
        #save the serializer, this returns the cluster model object that was created
        cluster = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(cluster.refid, "example_cluster_id")
    def test_serialization(self):
        #get the serializer class associated with clusters, create serializer with mock data and check validity
        serializer_class = serializers.serializer_class_lookup['clusters']
        data = copy.deepcopy(mockcluster)
        serializer = serializer_class(data=data)
        serializer.is_valid()
        #save the serializer, this returns the cluster model object that was created
        cluster = serializer.save()
        #verify the id matches that of our mock data
        self.assertEqual(cluster.refid, "example_cluster_id")
        #use the cluster serializer and check validity of returned serialized data
        serializer = serializers.ClusterSerializer(cluster)
        dictionary = serializer.data
        self.assertEqual("example_cluster_id", dictionary['id'])

 #testing multiple serializers in this class: AssetEnvironment Serializer, AssetGetEnvironment Serializer, AssetGetDetail Serializer
class AssetAdditionalSerializersTest(TestCase):
    def setUp(self):
        #create team
        Team.objects.create(refid="team-example-team")
        #create product
        Product.objects.create(refid="example-product", properties={"example": "test"})
        #create assettype, AppLanguage, Location, Entype
        AssetType.objects.create(id="svc", name="svc")
        AppLanguage.objects.create(id="python", name="python")
        Location.objects.create( name="example-location")
        EnvType.objects.create( id="example-env", name="example-env")
        #create product environment
        product = Product.objects.get(refid="example-product")
        location = Location.objects.get(name="example-location")
        env = EnvType.objects.get(name="example-env")
        ProductEnvironment.objects.create(refid="prod-environment", product=product, location_id=location.id, type_id=env.id)

    def test_assetenvironment_serialization(self):
        assetdata = copy.deepcopy(mockasset)
        asset_serializer_class = serializers.serializer_class_lookup['assets']
        assetserializer = asset_serializer_class(data=assetdata)
        assetserializer.is_valid()
        #save the serializer, this returns the asset model object that was created
        asset = assetserializer.save()
        prodenv = ProductEnvironment.objects.get(refid="prod-environment")
        #create assetenvironment
        AssetEnvironment.objects.create(refid="example-asset-environment", asset_id=asset.id, product_environment_id=prodenv.id)
        assetenvironment = AssetEnvironment.objects.get(refid="example-asset-environment")
        #use the serializer to take the created model and return serialized data
        serializer = serializers.AssetEnvironmentSerializer(assetenvironment)
        dictionary = serializer.data    
        self.assertEqual(dictionary['refid'], 'example-asset-environment')

    def test_assetgetenvironment_serialization(self):
        assetdata = copy.deepcopy(mockasset)
        asset_serializer_class = serializers.serializer_class_lookup['assets']
        assetserializer = asset_serializer_class(data=assetdata)
        assetserializer.is_valid()
        #save the serializer, this returns the asset model object that was created
        asset = assetserializer.save()
        #create product environment
        prodenv = ProductEnvironment.objects.get(refid="prod-environment")
        #create assetenvironment
        AssetEnvironment.objects.create(refid="example-asset-environment", asset_id=asset.id, product_environment_id=prodenv.id)
        assetenvironment = AssetEnvironment.objects.get(refid="example-asset-environment")
        #use the serializer to take the created model and return serialized data
        serializer = serializers.AssetEnvironmentSerializer(assetenvironment)
        dictionary = serializer.data    
        self.assertEqual(dictionary['refid'], 'example-asset-environment')
        #test get environment serializer
        getenvironmentserializer = serializers.AssetGetEnvironmentSerializer(asset)
        data = getenvironmentserializer.get_environments(asset)
        self.assertEqual(data[0]['id'], 'prod-environment')
    def test_assetgetdetail_serialization(self):
        assetdata = copy.deepcopy(mockasset)
        asset_serializer_class = serializers.serializer_class_lookup['assets']
        assetserializer = asset_serializer_class(data=assetdata)
        assetserializer.is_valid()
        #save the serializer, this returns the asset model object that was created
        asset = assetserializer.save()
        #create product environment
        prodenv = ProductEnvironment.objects.get(refid="prod-environment")
        #create assetenvironment
        AssetEnvironment.objects.create(refid="example-asset-environment", asset_id=asset.id, product_environment_id=prodenv.id)
        #test asset get detail serializer
        assetgetdetailserializer = serializers.AssetGetDetailSerializer(asset)
        data = assetgetdetailserializer.data
        self.assertEqual(data['team_name'], 'team-example-team')
        self.assertEqual(data['product_name'], 'example-product')
   

   #test this w added resource
    def test_assetenvironmentattaches_serialization(self):
        assetdata = copy.deepcopy(mockasset)
        asset_serializer_class = serializers.serializer_class_lookup['assets']
        assetserializer = asset_serializer_class(data=assetdata)
        assetserializer.is_valid()
        #save the serializer, this returns the asset model object that was created
        asset = assetserializer.save()
        #create product environment
        prodenv = ProductEnvironment.objects.get(refid="prod-environment")
        #create assetenvironment
        AssetEnvironment.objects.create(refid="example-asset-environment", asset_id=asset.id, product_environment_id=prodenv.id)
        #test asset get detail serializer
        team = Team.objects.get(refid="team-example-team")
        location = Location.objects.get(name="example-location")
        assetenvironment = AssetEnvironment.objects.get(refid="example-asset-environment")
        Resource.objects.create(refid="example-resource", owner=team, location=location)
        resource = Resource.objects.get(refid="example-resource")
        resource.assetEnvironments.set([assetenvironment])
        assetbyenvironmentserializer = serializers.AssetEnvironmentAttachesSerializer(assetenvironment)
        data = assetbyenvironmentserializer.get_resources(assetenvironment)
        self.assertEqual(data[0], 'example-resource')
   
class ProductEnvironmentSerializersTest(TestCase):
    def setUp(self):
        #create product
        Product.objects.create(refid="example-product", properties={"example": "test"})
        #create assettype, AppLanguage, Location, Entype
        AssetType.objects.create(id="svc", name="svc")
        AppLanguage.objects.create(id="python", name="python")
        Location.objects.create( name="example-location")
        EnvType.objects.create( id="example-env", name="example-env")
        #create product environment
        product = Product.objects.get(refid="example-product")
        location = Location.objects.get(name="example-location")
        env = EnvType.objects.get(name="example-env")
        ProductEnvironment.objects.create(refid="prod-environment", product=product, location_id=location.id, type_id=env.id)
    def test_productenvironmentget_serialization(self):
        productenv = ProductEnvironment.objects.get(refid="prod-environment")
        productenvironmentgetserializer = serializers.ProductEnvironmentGetSerializer(productenv)
        data = productenvironmentgetserializer.data 
        #verify that serializer returned correct data
        self.assertEqual(data['id'], 'prod-environment')
        self.assertEqual(data['type'], 'example-env')        
    def test_productenvironmentgetdetail_serialization(self):
        productenv = ProductEnvironment.objects.get(refid="prod-environment")
        productenvironmentgetdetailserializer = serializers.ProductEnvironmentGetDetailSerializer(productenv)
        data = productenvironmentgetdetailserializer.data 
        #uuid comes back as id with getdetailserializer, so check refid instead of id
        self.assertEqual(data['refid'], 'prod-environment')
        self.assertEqual(data['type'], 'example-env')        