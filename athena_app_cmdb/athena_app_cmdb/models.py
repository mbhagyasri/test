# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global.
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================
import uuid
from django.db import models
from requests.structures import CaseInsensitiveDict
from django.core.exceptions import FieldDoesNotExist

athena_app_cmdb_API_PATH = ''


class AppLanguage(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=100)
    name = models.CharField(db_column='name', max_length=100)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    created_by = models.CharField(db_column='created_by')
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'app_language'
        verbose_name = 'App Language'

    def __str__(self):
        return self.name


class AssetType(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=100)
    name = models.CharField(db_column='name', max_length=100)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

    class Meta:
        db_table = 'asset_type'

    def __str__(self):
        return self.name


class Cluster(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=100)
    uri = models.CharField(db_column='uri', max_length=100)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

    class Meta:
        managed = True
        db_table = 'cluster'
        verbose_name = 'Kubernetes Cluster'
        ordering = ['-updated_at', '-created_at', ]


    @property
    def self_links(self):
        links = '%s/clusters/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


class DatabaseChangeLogLock(models.Model):
    id = models.IntegerField(db_column='id', primary_key=True)
    locked = models.BooleanField(db_column='locked')
    lockgranted = models.DateTimeField(db_column='lockgranted', blank=True, null=True)
    lockedby = models.CharField(db_column='lockedby', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'databasechangeloglock'
        verbose_name = 'Database Change Log Lock'

    def __str__(self):
        return self.name


class EnvType(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=50)
    name = models.CharField(db_column='name', max_length=50)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

    class Meta:
        db_table = 'env_type'
        verbose_name = 'Environment Type'

    def __str__(self):
        return self.name


class LocationRegion(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=50)
    name = models.CharField(db_column='name', max_length=50)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

    class Meta:
        db_table = 'location_region'
        verbose_name = 'Location Region'

    def __str__(self):
        return self.name


class LocationStatus(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=50)
    name = models.CharField(db_column='name', max_length=50)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

    class Meta:
        db_table = 'location_status'
        verbose_name = 'Location Status'

    def __str__(self):
        return self.name


class Location(models.Model):
    id = models.CharField(db_column='id', max_length=100, primary_key=True)
    name = models.CharField(db_column='name', max_length=100, unique=True)
    env_type = models.ForeignKey(EnvType, db_column='env_type_id', blank=True, null=True, on_delete=models.SET_NULL)
    domain = models.CharField(db_column='domain', max_length=100)
    status = models.ForeignKey(LocationStatus, db_column='status', blank=True, null=True, on_delete=models.SET_NULL)
    region = models.ForeignKey(LocationRegion, db_column='region', blank=True, null=True, on_delete=models.SET_NULL)
    parameters = models.TextField(db_column='parameters')
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

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
        return self.name


class Team(models.Model):
    id = models.CharField(db_column='id', max_length=100, primary_key=True)
    name = models.CharField(db_column='name', max_length=100, unique=True)
    email = models.CharField(db_column='email', max_length=255)
    ad_group = models.CharField(db_column='ad_group', max_length=255)
    notification = models.CharField(db_column='notification', max_length=255)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

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
        return self.name


class Product(models.Model):
    id = models.CharField(db_column='id', max_length=100, primary_key=True)
    external_ids = models.JSONField(db_column='external_ids')
    environments = models.JSONField(db_column='environments')
    security = models.JSONField(db_column='security')
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

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
        return self.name


class Asset(models.Model):
    id = models.CharField(db_column='id', max_length=100, primary_key=True)
    name = models.CharField(db_column='app_name', max_length=255, unique=True)
    product = models.ForeignKey(Product, db_column='product_id', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, db_column='team_id', on_delete=models.CASCADE)
    type = models.ForeignKey(AssetType, db_column='asset_type_id', on_delete=models.CASCADE)
    appLanguage = models.ForeignKey(AppLanguage, db_column='app_language_id', blank=True, null=True,
                                    on_delete=models.SET_NULL)
    repo = models.CharField(db_column='repo', max_length=200)
    assetMasterId = models.IntegerField(db_column='asset_master_id', blank=True, null=True)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)


    class Meta:
        managed = True
        db_table = 'asset'
        verbose_name = 'Asset'
        ordering = ['-updated_at', '-created_at', ]


    @property
    def self_links(self):
        links = '%s/assets/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.name


class AssetBackup(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=100)
    name = models.CharField(db_column='app_name', max_length=255, unique=True)
    product = models.ForeignKey(Product, db_column='product_id', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, db_column='team_id', on_delete=models.CASCADE)
    type = models.ForeignKey(AssetType, db_column='asset_type_id', on_delete=models.CASCADE)
    appLanguage = models.ForeignKey(AppLanguage, db_column='app_language_id', on_delete=models.CASCADE)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    repo = models.CharField(db_column='repo', max_length=200, blank=True, null=True)
    assetMasterId = models.IntegerField(db_column='asset_master_id')
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

    class Meta:
        managed = True
        db_table = 'asset_backup'
        verbose_name = 'Asset Backup'
        ordering = ['-updated_at', '-created_at', ]


class Resource(models.Model):
    id = models.CharField(db_column='id', max_length=100, primary_key=True)
    type = models.CharField(db_column='type', max_length=100)
    owner = models.ForeignKey(Team, db_column='owner', blank=True, null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(Location, db_column='location', blank=True, null=True, on_delete=models.SET_NULL)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)

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
        return self.name


class SecurityProvider(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=100)
    schemes = models.CharField(db_column='schemes', max_length=30)
    properties = models.JSONField(db_column='json', blank=True, null=True)
    created_at = models.DateTimeField(db_column='ins_gmt_ts', blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_column='upd_gmt_ts', blank=True, null=True, auto_now=True)
    deleted = models.CharField(db_column='del_ind', max_length=1, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'securityprovider'
        verbose_name = 'Security Provider'

    def __str__(self):
        return self.name


@classmethod
def model_field_exists(cls, field):
    try:
        cls._meta.get_field(field)
        return True
    except FieldDoesNotExist:
        return False


models_mapping = {'locations': Location,  'teams': Team,
                  'clusters': Cluster, 'products': Product, 'assets': Asset, 'resources': Resource,
                  'asset_types': AssetType
                  }
models_name_mapping = {'locations': 'Location', 'teams': 'Team',
                       'clusters': 'Cluster', 'products': 'Product', 'assets': 'Asset', 'resources': 'Resource',
                       'asset_types': AssetType
                       }

models_class_lookup = CaseInsensitiveDict(models_mapping)
models_name_lookup = CaseInsensitiveDict(models_name_mapping)
models.Model.field_exists = model_field_exists

