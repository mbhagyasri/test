# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global.
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================
import uuid
from django.db import models
from requests.structures import CaseInsensitiveDict
from django.core.exceptions import FieldDoesNotExist

athena_app_cmdb_API_PATH = '/api'


class Location(models.Model):
    internal_id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    id = models.CharField(db_column='old_version_id', max_length=50)
    name = models.CharField(db_column='name', max_length=255, unique=True)
    properties = models.JSONField(db_column='properties', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)
    deleted_at = models.DateTimeField(db_column='deleted_at', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Location'
        verbose_name = 'Location'
        ordering = ['-updated_at', '-created_at', ]
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_location_name')
        ]

    @property
    def self_links(self):
        links = '%s/locations/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.name


class Cluster(models.Model):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    name = models.CharField(db_column='name', max_length=255, unique=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    properties = models.JSONField(db_column='properties', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)
    deleted_at = models.DateTimeField(db_column='deleted_at', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Cluster'
        verbose_name = 'Kubernetes Cluster'
        ordering = ['-updated_at', '-created_at', ]
        constraints = [
            models.UniqueConstraint(fields=['name','location'], name='unique_cluster_name')
        ]

    @property
    def self_links(self):
        links = '%s/clusters/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.name


class Team(models.Model):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    name = models.CharField(db_column='name', max_length=255, unique=True)
    properties = models.JSONField(db_column='properties', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)
    deleted_at = models.DateTimeField(db_column='deleted_at', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Team'
        verbose_name = 'Team'
        ordering = ['-updated_at', '-created_at',]
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_team_name')
        ]

    @property
    def self_links(self):
        links = '%s/teams/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    name = models.CharField(db_column='name', max_length=255, unique=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    properties = models.JSONField(db_column='properties', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)
    deleted_at = models.DateTimeField(db_column='deleted_at', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Product'
        verbose_name = 'Product'
        ordering = ['-updated_at', '-created_at',]
        constraints = [
            models.UniqueConstraint(fields=['name', 'location'], name='unique_product_name')
        ]

    @property
    def self_links(self):
        links = '%s/products/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.name

class Asset(models.Model):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    name = models.CharField(db_column='name', max_length=255, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    clusters = models.ManyToManyField(Cluster)
    properties = models.JSONField(db_column='properties', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)
    deleted_at = models.DateTimeField(db_column='deleted_at', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Asset'
        verbose_name = 'Asset'
        ordering = ['-updated_at', '-created_at', ]


    @property
    def self_links(self):
        links = '%s/assets/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.name


class Resource(models.Model):
    id = models.UUIDField(db_column='id', primary_key=True, default=uuid.uuid4)
    name = models.CharField(db_column='name', max_length=255, unique=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    properties = models.JSONField(db_column='properties', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default='f')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True, auto_now_add=True)
    created_by = models.CharField(db_column='created_by', max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(db_column='updated_at', blank=True, null=True, auto_now=True)
    updated_by = models.CharField(db_column='updated_by', max_length=100, blank=True, null=True)
    deleted_at = models.DateTimeField(db_column='deleted_at', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Resource'
        verbose_name = 'Resource'
        ordering = ['-updated_at', '-created_at',]

    @property
    def self_links(self):
        links = '%s/resources/%s' % (athena_app_cmdb_API_PATH, self.id)
        return links

    def __str__(self):
        return self.name


class AssetType(models.Model):
    id = models.CharField(db_column='id', primary_key=True, max_length=50)
    name = models.CharField(db_column='name', max_length=50)
    class Meta:
        managed = False
        db_table = 'asset_type'


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

