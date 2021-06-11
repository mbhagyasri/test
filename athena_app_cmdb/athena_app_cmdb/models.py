# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global.
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================
import uuid
import os
import json
import logging
import jsonschema
from django.db import models
from requests.structures import CaseInsensitiveDict
from django.core.exceptions import FieldDoesNotExist
from .softdelete.models import SoftDeleteModel
from .middleware import ViewException


logger = logging.getLogger(__name__)
FORMAT = 'json'
athena_app_cmdb_API_PATH = ''
UUID_MODELS = ['assets', 'clusters', 'locations', 'teams', 'products', 'resources']


def validate_json(objname, instance, raise_exception=True):
    mapping = {
        "locations": 'Location.json', "products": 'Product.json', "resources": "Resource.json",
        "assets-bff": 'Bff.json', "assets-app": "App.json", "assets-svc": "Svc.json",
        "teams": 'Team.json',
        "assetsByEnvironment-bff": 'Bff.json', "assetsByEnvironment-app": "App.json",
        "assetsByEnvironment-svc": "Svc.json",
        "clusters": 'Cluster.json'
    }
    if objname == 'assets' or objname == 'assetsByEnvironment':
        filename = mapping.get('{}-{}'.format(objname, instance.get('type')), None)
    else:
        filename = mapping.get(objname, None)
    if not filename:
        # ignore schema validations
        return True, 'Ignore'
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    file_path = str(os.path.join(__location__, "ui/api-docs/json-schemas", filename))

    try:
        with open(file_path) as data_file:
            json_schema = json.load(data_file)
    except Exception as e:
        logger.exception(e)
        error_message = "Failed to read json-schemas for validation."
        if raise_exception:
            raise ViewException(FORMAT, error_message, 400)
        else:
            return False, error_message

    try:
        jsonschema.validate(instance=instance, schema=json_schema)
    except jsonschema.exceptions.ValidationError as err:
        if raise_exception:
            raise ViewException(FORMAT, str(err), 400)
        else:
            return False, str(err)
    return True, 'OK'


class AppLanguage(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=100)
    name = models.CharField(db_column='name', max_length=100)
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    deleted = models.BooleanField(db_column='deleted', default='f')


    class Meta:
        managed = True
        db_table = 'app_language'
        verbose_name = 'App Language'

    def __str__(self):
        return self.name


class AssetType(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=100)
    name = models.CharField(db_column='name', max_length=100)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'asset_type'

    def __str__(self):
        return self.name

    @property
    def need_merge_properties(self):
        return False


class Cluster(SoftDeleteModel):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    refid = models.CharField(db_column='cluster_id', unique=True, max_length=100)
    uri = models.CharField(db_column='uri', max_length=100)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cluster'
        verbose_name = 'Kubernetes Cluster'
        ordering = ['-updated_at', '-created_at', ]


    @property
    def self_links(self):
        links = '%s/clusters/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links


class DatabaseChangeLog(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=255)
    author = models.CharField(db_column='author', max_length=255)
    filename = models.CharField(max_length=255)
    dateexecuted = models.DateTimeField(db_column='dateexecuted', auto_now_add=True)
    orderexecuted = models.IntegerField(db_column='orderexecuted')
    exectype = models.CharField(db_column='exectype', max_length=10)
    md5sum = models.CharField(db_column='md5sum', max_length=35, blank=True, null=True)
    description = models.CharField(db_column='description', max_length=255, blank=True, null=True)
    comments = models.CharField(db_column='comments', max_length=255, blank=True, null=True)
    tag = models.CharField(db_column='tag', max_length=255, blank=True, null=True)
    liquibase = models.CharField(db_column='liquibase', max_length=20, blank=True, null=True)
    contexts = models.CharField(db_column='contexts', max_length=255, blank=True, null=True)
    labels = models.CharField(db_column='labels', max_length=255, blank=True, null=True)
    deployment_id = models.CharField(db_column='deployment_id', max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'databasechangelog'
        verbose_name = 'Database Change Log'


class DatabaseChangeLogLock(models.Model):
    id = models.IntegerField(db_column='id', primary_key=True)
    locked = models.BooleanField(db_column='locked')
    lockgranted = models.DateTimeField(db_column='lockgranted', blank=True, null=True)
    lockedby = models.CharField(db_column='lockedby', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'databasechangeloglock'
        verbose_name = 'Database Change Log Lock'


    @property
    def need_merge_properties(self):
        return False


class EnvType(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=50)
    name = models.CharField(db_column='name', max_length=50)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'env_type'
        verbose_name = 'Environment Type'

    def __str__(self):
        return self.name


class LocationRegion(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=50)
    name = models.CharField(db_column='name', max_length=50)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'location_region'
        verbose_name = 'Location Region'

    def __str__(self):
        return self.name


class LocationStatus(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=50)
    name = models.CharField(db_column='name', max_length=50)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'location_status'
        verbose_name = 'Location Status'

    def __str__(self):
        return self.name


class Location(SoftDeleteModel):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    refid = models.CharField(db_column='location_id', max_length=100, unique=True)
    name = models.CharField(db_column='name', max_length=100, unique=True)
    env_type = models.ForeignKey(EnvType, db_column='env_type_id', blank=True, null=True, on_delete=models.SET_NULL)
    domain = models.CharField(db_column='domain', max_length=100)
    status = models.ForeignKey(LocationStatus, db_column='status', blank=True, null=True, on_delete=models.SET_NULL)
    region = models.ForeignKey(LocationRegion, db_column='region', blank=True, null=True, on_delete=models.SET_NULL)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)

    class Meta:
        managed = True
        db_table = 'location'
        verbose_name = 'Location'
        ordering = ['-updated_at', '-created_at', ]

    @property
    def self_links(self):
        links = '%s/locations/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.refid


class Team(SoftDeleteModel):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    refid = models.CharField(db_column='team_id', max_length=100, unique=True)
    name = models.CharField(db_column='name', max_length=100, unique=True)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'team'
        verbose_name = 'Team'
        ordering = ['-updated_at', '-created_at', ]

    @property
    def self_links(self):
        links = '%s/teams/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.refid


class Product(SoftDeleteModel):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    refid = models.CharField(db_column='product_id', max_length=100, unique=True)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'product'
        verbose_name = 'Product'
        ordering = ['-updated_at', '-created_at',]

    @property
    def self_links(self):
        links = '%s/products/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.refid


class ProductEnvironment(models.Model):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    refid = models.CharField(db_column='environment_id', max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='environments', blank=True, null=True)
    type = models.ForeignKey(EnvType, on_delete=models.PROTECT)
    prefix = models.CharField(db_column='prefix', max_length=50, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'product_environment'
        verbose_name = 'Environment'
        ordering = ['product', 'type']
        unique_together = ('refid', 'product')

    def __str__(self):
        return self.refid


class Asset(SoftDeleteModel):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    refid = models.CharField(db_column='asset_id', max_length=100, unique=True)
    name = models.CharField(db_column='app_name', max_length=255)
    product = models.ForeignKey(Product, db_column='product_id', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, db_column='team_id', on_delete=models.CASCADE)
    type = models.ForeignKey(AssetType, db_column='asset_type_id', on_delete=models.CASCADE)
    appLanguage = models.ForeignKey(AppLanguage, db_column='app_language_id', blank=True, null=True,
                                    on_delete=models.SET_NULL)
    repo = models.CharField(db_column='repo', max_length=200)
    assetMasterId = models.IntegerField(db_column='asset_master_id', blank=True, null=True)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'asset'
        verbose_name = 'Asset'
        unique_together = ("id", "name")
        ordering = ['-updated_at', '-created_at', ]

    @property
    def self_links(self):
        links = '%s/assets/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.name


class AssetEnvironment(SoftDeleteModel):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    refid = models.CharField(db_column='environment_id', max_length=100)
    product_environment = models.ForeignKey(ProductEnvironment, on_delete=models.PROTECT)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='environments')
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'asset_environment'
        verbose_name = 'Environment'
        unique_together = ("refid", "asset")

    def __str__(self):
        return self.refid

class Resource(SoftDeleteModel):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    refid = models.CharField(db_column='resource_id', max_length=100, unique=True)
    owner = models.ForeignKey(Team, db_column='owner', blank=True, null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(Location, db_column='location', blank=True, null=True, on_delete=models.SET_NULL)
    assetEnvironments = models.ManyToManyField(AssetEnvironment, related_name='resources', blank=True)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'resource'
        verbose_name = 'Resource'
        ordering = ['-updated_at', '-created_at',]

    @property
    def self_links(self):
        links = '%s/resources/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.refid


class SecurityProvider(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=100)
    schemes = models.CharField(db_column='schemes', max_length=30)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'securityprovider'
        verbose_name = 'Security Provider'


models_mapping = {'locations': Location,  'teams': Team, 'securityProviders': SecurityProvider,
                  'clusters': Cluster, 'products': Product, 'assets': Asset, 'resources': Resource,
                  'asset_types': AssetType, 'assetsByEnvironment': AssetEnvironment
                  }
models_name_mapping = {'locations': 'Location', 'teams': 'Team', 'securityProviders': SecurityProvider,
                       'clusters': 'Cluster', 'products': 'Product', 'assets': 'Asset', 'resources': 'Resource',
                       'asset_types': AssetType, 'assetsByEnvironment': AssetEnvironment
                       }

models_class_lookup = CaseInsensitiveDict(models_mapping)
models_name_lookup = CaseInsensitiveDict(models_name_mapping)
