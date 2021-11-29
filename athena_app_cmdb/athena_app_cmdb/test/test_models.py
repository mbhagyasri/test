# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

from django.test import TestCase
from athena_app_cmdb.models import Location, AppLanguage, AssetType, Cluster

class LocationModelTests(TestCase):
    def setUp(self):
        Location.objects.create(refid="us-west-2", name="Oregon")

    def test_location_exist(self):
        location = Location.objects.get(refid="us-west-2")
        self.assertEqual(location.name, "Oregon")

    def test_string_representation(self):
        location = Location(refid="us-west-2", name="Oregon")
        self.assertEqual(str(location), location.refid)

class AppLanguageTests(TestCase):
    def setUp(self):
        AppLanguage.objects.create(id="java-8.1", name="Java")
    
    def test_app_language_exists(self):
        app_language = AppLanguage.objects.get(id="java-8.1")
        self.assertEqual(app_language.id, "java-8.1")
    
    def test_string_representation(self):
        app_language = AppLanguage(id="java-8.1", name="Java")
        self.assertEqual(str(app_language), app_language.name)

class AssetTypeTests(TestCase):
    def setUp(self):
        AssetType.objects.create(id="athena-asset-2", name="Athena PCP")
    
    def test_asset_type_exists(self):
        asset_type = AssetType.objects.get(id="athena-asset-2")
        self.assertEqual(asset_type.id, "athena-asset-2")
    
    def test_string_representation(self):
        asset_type = AssetType(id="athena-asset-2", name="Athena PCP")
        self.assertEqual(str(asset_type), asset_type.name)
    
    def test_need_merge_properties(self):
        asset_type = AssetType(id="athena-asset-2", name="Athena PCP")
        function_value = asset_type.need_merge_properties
        message = "Test value is not false."
        self.assertFalse(function_value, message)

class ClusterTests(TestCase):
    def setUp(self):
        Cluster.objects.create(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000", refid="cluster_2", uri="example-cluster-uri.com/api")
    
    def test_cluster_exists(self):
        cluster = Cluster.objects.get(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000")
        self.assertEqual(cluster.refid, "cluster_2")
    
    def test_self_links(self):
        cluster = Cluster(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000", refid="cluster_2", uri="example-cluster-uri.com/api")
        link = "/clusters/11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000"
        self.assertEqual(cluster.self_links, link)


    

