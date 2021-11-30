# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

from django.test import TestCase
from athena_app_cmdb.models import Location, AppLanguage, AssetType, Cluster, DatabaseChangeLog, DatabaseChangeLogLock, EnvType, LocationRegion, LocationStatus, Team, Product, ProductEnvironment


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
    
class DatabaseChangeLogModelTests(TestCase):
    def setUp(self):
        DatabaseChangeLog.objects.create(id=1, author="tuc", filename="metrics-changelog", orderexecuted=3)
    
    def test_database_changelog_exists(self):
        database_changelog = DatabaseChangeLog.objects.get(id=1)
        self.assertEqual(database_changelog.author, "tuc")
    
class DatabaseChangeLogLockModelTests(TestCase):
    def setUp(self):
        DatabaseChangeLogLock.objects.create(id=2, locked=False)

    def test_database_changelog_lock_exists(self):
        database_changelog_lock = DatabaseChangeLogLock.objects.get(id=2)
        self.assertEqual(database_changelog_lock.locked, False)

    def test_need_merge_properties(self):
        database_changelog_lock = DatabaseChangeLogLock(id=2, locked=False)
        function_value = database_changelog_lock.need_merge_properties
        message = "Test value is not false."
        self.assertFalse(function_value, message)
    
class EnvTypeModelTests(TestCase):
    def setUp(self):
        EnvType.objects.create(id=10, name="prod", deleted='f')
    
    def test_env_type_exists(self):
        env_type = EnvType.objects.get(id=10)
        self.assertEqual(env_type.name, "prod")
    
    def test_string_representation(self):
        env_type = EnvType.objects.get(id=10)
        self.assertEqual(str(env_type), "prod")

class LocationRegionModelTests(TestCase):
    def setUp(self):
        LocationRegion.objects.create(id=7, name="us-west", deleted='f')
    
    def test_location_region_exists(self):
        location_region = LocationRegion.objects.get(id=7)
        self.assertEqual(location_region.name, "us-west")
    
    def test_string_representation(self):
        location_region = LocationRegion.objects.get(id=7)
        self.assertEqual(str(location_region), "us-west")

class LocationStatusModelTests(TestCase):
    def setUp(self):
        LocationStatus.objects.create(id=5, name="online", deleted='t')

    def test_location_status_exists(self):
        location_status = LocationStatus.objects.get(id=5)
        self.assertEqual(location_status.name, "online")
    
    def test_string_representation(self):
        location_status = LocationStatus.objects.get(id=5)
        self.assertEqual(str(location_status), "online")

class LocationModelTests(TestCase):
    def setUp(self):
        Location.objects.create(refid="us-west-2", name="Oregon")

    def test_location_exist(self):
        location = Location.objects.get(refid="us-west-2")
        self.assertEqual(location.name, "Oregon")

    def test_string_representation(self):
        location = Location(refid="us-west-2", name="Oregon")
        self.assertEqual(str(location), location.refid)

class TeamModelTests(TestCase):
    def setUp(self):
        Team.objects.create(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000", refid="team-10", name="fortellis")
    
    def test_team_exists(self):
        team = Team.objects.get(refid="team-10")
        self.assertEqual(team.name, "fortellis")

    def test_self_links(self):
        team = Team.objects.get(refid="team-10")
        links = "/teams/11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000"
        self.assertEqual(team.self_links, links)
    
    def test_string_representation(self):
        team = Team.objects.get(name="fortellis")
        self.assertEqual(str(team), team.refid)

class ProductModelTests(TestCase):
    def setUp(self):
        Product.objects.create(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000", refid="dms")

    def test_product_exists(self):
        product = Product.objects.get(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000")
        self.assertEqual(product.refid, "dms")
    
    def test_string_representation(self):
        product = Product.objects.get(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000")
        self.assertEqual(str(product), product.refid)

class ProductEnvironmentModelTests(TestCase):
    def setUp(self):
        Location.objects.create(refid="us-west-2", name="Oregon")
        EnvType.objects.create(id=10, name="prod", deleted='f')
        ProductEnvironment.objects.create(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000", refid="dev", location=Location.objects.get(refid="us-west-2"), type=EnvType.objects.get(id=10))

    def test_product_exists(self):
        product_environment = ProductEnvironment.objects.get(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000")
        self.assertEqual(product_environment.refid, "dev")
    
    def test_string_representation(self):
        product_environment = ProductEnvironment.objects.get(id="11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000")
        self.assertEqual(str(product_environment), product_environment.refid)

    

