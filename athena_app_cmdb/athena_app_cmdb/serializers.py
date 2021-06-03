# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================
import pydash
import logging

from collections import OrderedDict
from rest_framework import serializers
from . import models
from copy import deepcopy
from requests.structures import CaseInsensitiveDict

logger = logging.getLogger(__name__)


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssetType
        fields = '__all__'


class AssetSerializer(serializers.ModelSerializer):
    cicd = serializers.CharField(required=False)
    attaches = serializers.JSONField(required=False)
    consumes = serializers.JSONField(required=False)
    internal = serializers.JSONField(required=False)
    security = serializers.JSONField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = models.Asset
        fields = '__all__'

    def to_representation(self, instance):
        return AssetGetSerializer(instance).data

    def to_internal_value(self, data):
        fields = [f.name for f in models.Asset._meta.fields + models.Asset._meta.many_to_many]
        properties = data.get('properties', {})
        data_copy = deepcopy(data)
        for key in data_copy:
            if key == 'env-type':
                key = 'env_type'
            if key not in fields:
                properties[key] = data[key]
                del data[key]
        data['properties'] = properties
        return super(AssetSerializer, self).to_internal_value(data)


class AssetGetDetailSerializer(serializers.ModelSerializer):
    cicd = serializers.CharField(source='properties.cicd', required=False)
    attaches = serializers.JSONField(source='properties.attaches', required=False)
    consumes = serializers.JSONField(source='properties.consumes', required=False)
    internal = serializers.JSONField(source='properties.internal', required=False)
    security = serializers.JSONField(source='properties.security', required=False)
    description = serializers.CharField(source='properties.description', required=False)

    class Meta:
        model = models.Asset
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        properties = data.pop('properties', None)
        data.update(properties)
        return data

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks


class AssetGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Asset
        fields = ('id', 'name', 'repo', 'team', 'type',
                  'product',
                  'appLanguage',  'assetMasterId', 'properties', 'deleted')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        properties = data.pop('properties', None)
        data.update(properties)
        return data

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks


class AssetGetEnvironmentSerializer(serializers.ModelSerializer):
    environments = serializers.SerializerMethodField()

    class Meta:
        model = models.Asset
        fields = ('environments',)

    def get_environments(self, instance):
        product = ProductGetSerializer(instance.product).data
        data = product.get('environments', [])
        return data


class AssetGetUrlSerializer(serializers.ModelSerializer):
    locations = serializers.SerializerMethodField()
    environments = serializers.SerializerMethodField()

    class Meta:
        model = models.Asset
        fields = ('id', 'name', 'environments', 'locations', 'properties', 'type', 'product')

    def get_environments(self, instance):
        product = ProductGetSerializer(instance.product).data
        data = product.get('environments', [])
        return data

    def get_locations(self, instance):
        data = []
        product = ProductGetSerializer(instance.product).data
        environments = product.get('environments', [])
        if environments:
            for env in environments:
                if models.Location.objects.filter(id=env.get('location')).exists():
                    loc = models.Location.objects.get(id=env.get('location'))
                    location = LocationGetSerializer(loc).data
                    data.append(location)
        return data

    def to_representation(self, instance):
        return_data = []
        data = super().to_representation(instance)
        environments = data.get('environments', [])
        locations = data.get('locations', [])
        if not environments:
            return {}
        for env in environments:
            tmp_data = OrderedDict([('environment_id', env['id']), ('type', env['type'])])
            prefix = "" if env['type'] == 'prod' else env['id'] + '-'
            hostname = data['name'] if data['type'] != 'bff' else '{}-{}.sd'.format(data['product'],
                                                                                    data['id'])

            additional_urls = []
            if locations:
                for loc in locations:
                    if loc.get('id') == env['location']:
                        url = 'https://{}{}.{}'.format(prefix, hostname, loc.get('domain', ""))
                        tmp_data['url'] = url
            if pydash.objects.has(data, 'properties.additionalUrls'):
                for url in pydash.objects.get(data, 'properties.additionalUrls', []):
                    if url.get('environment') == env['id']:
                        additional_urls = url.get('entries', [])
            tmp_data['additionalUrls'] = additional_urls
            return_data.append(tmp_data)
        return {'urls': return_data}




class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Location
        fields = '__all__'

    def to_representation(self, instance):
        return LocationGetSerializer(instance).data

    def to_internal_value(self, data):
        fields = [f.name for f in models.Location._meta.fields + models.Location._meta.many_to_many]
        properties = data.get('properties', {})
        data_copy = deepcopy(data)
        for key in data_copy:
            if key == 'env-type':
                key = 'env_type'
            if key not in fields:
                properties[key] = data[key]
                del data[key]
        data['properties'] = properties
        return super(LocationSerializer, self).to_internal_value(data)


class LocationGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Location
        fields = ('id', 'name', 'domain', 'region', 'status',
                  'env_type', 'properties',
                  )

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'env_type' in data:
            env_type = data.pop('env_type')
            data['env-type'] = env_type
        properties = data.pop('properties', None)
        data.update(properties)
        return data


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cluster
        fields = '__all__'

    def to_representation(self, instance):
        return ClusterGetSerializer(instance).data

    def to_internal_value(self, data):
        fields = [f.name for f in models.Cluster._meta.fields + models.Cluster._meta.many_to_many]
        properties = data.get('properties', {})
        data_copy = deepcopy(data)
        for key in data_copy:
            if key == 'env-type':
                key = 'env_type'
            if key not in fields:
                properties[key] = data[key]
                del data[key]
        data['properties'] = properties
        return super(ClusterSerializer, self).to_internal_value(data)


class ClusterGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Cluster
        fields = ('id', 'uri', 'properties',)

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'env_type' in data:
            env_type = data.pop('env_type')
            data['env-type'] = env_type
        properties = data.pop('properties', None)
        data.update(properties)
        return data


class ProductSerializer(serializers.ModelSerializer):
    attaches = serializers.JSONField(required=False)
    consumes = serializers.JSONField(required=False)
    internal = serializers.JSONField(required=False)
    security = serializers.JSONField(required=False)
    description = serializers.CharField(required=False)
    class Meta:
        model = models.Product
        fields = '__all__'

    def to_representation(self, instance):
        return ProductGetSerializer(instance).data
    
    def to_internal_value(self, data):
        fields = [f.name for f in models.Product._meta.fields + models.Product._meta.many_to_many]
        properties = data.get('properties', {})
        data_copy = deepcopy(data)
        for key in data_copy:
            if key == 'env-type':
                key = 'env_type'
            if key not in fields:
                properties[key] = data[key]
                del data[key]
        data['properties'] = properties
        return super(ProductSerializer, self).to_internal_value(data)


class ProductGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Product
        fields = ('id', 'properties')

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'env_type' in data:
            env_type = data.pop('env_type')
            data['env-type'] = env_type
        properties = data.pop('properties', None)
        data.update(properties)
        return data


class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Resource
        fields = '__all__'

    def to_representation(self, instance):
        return ResourceGetSerializer(instance).data

    def to_internal_value(self, data):
        fields = [f.name for f in models.Resource._meta.fields + models.Resource._meta.many_to_many]
        properties = data.get('properties', {})
        data_copy = deepcopy(data)
        for key in data_copy:
            if key == 'env-type':
                key = 'env_type'
            if key not in fields:
                properties[key] = data[key]
                del data[key]
        data['properties'] = properties
        return super(ResourceSerializer, self).to_internal_value(data)


class ResourceGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Resource
        fields = ('id', 'type', 'owner', 'location', 'properties',
                  )

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'env_type' in data:
            env_type = data.pop('env_type')
            data['env-type'] = env_type
        properties = data.pop('properties', None)
        data.update(properties)
        return data


class TeamSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    notification = serializers.ListField(required=False)

    class Meta:
        model = models.Team
        fields = '__all__'

    def to_representation(self, instance):
        return TeamGetSerializer(instance).data

    def to_internal_value(self, data):
        fields = [f.name for f in models.Team._meta.fields + models.Team._meta.many_to_many]
        properties = data.get('properties', {})
        data_copy = deepcopy(data)
        for key in data_copy:
            if key == 'env-type':
                key = 'env_type'
            if key not in fields:
                properties[key] = data[key]
                del data[key]
        data['properties'] = properties
        return super(TeamSerializer, self).to_internal_value(data)



class SecurityProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SecurityProvider
        fields = '__all__'

    def to_representation(self, instance):
        return SecurityProviderGetSerializer(instance).data

    def to_internal_value(self, data):
        fields = [f.name for f in models.SecurityProvider._meta.fields + models.SecurityProvider._meta.many_to_many]
        properties = data.get('properties', {})
        data_copy = deepcopy(data)
        for key in data_copy:
            if key == 'env-type':
                key = 'env_type'
            if key not in fields:
                properties[key] = data[key]
                del data[key]
        data['properties'] = properties
        return super(SecurityProviderSerializer, self).to_internal_value(data)


class SecurityProviderGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SecurityProvider
        fields = ('id', 'schemes', 'properties',
                  )

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'env_type' in data:
            env_type = data.pop('env_type')
            data['env-type'] = env_type
        properties = data.pop('properties', None)
        data.update(properties)
        return data


class TeamGetSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source='properties.email', required=False)
    description = serializers.ReadOnlyField(source='properties.description', required=False)
    notification = serializers.ReadOnlyField(source='properties.notification', required=False)

    class Meta:
        model = models.Team
        fields = ('id', 'name',
                  'email', 'description', 'notification', 'properties',
                    'updated_at', 'updated_by',
                  'created_at', 'created_by', 'deleted',)

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'env_type' in data:
            env_type = data.pop('env_type')
            data['env-type'] = env_type
        properties = data.pop('properties', None)
        data.update(properties)
        return data


serializers_mapping = {
    'assets': AssetSerializer,
    'locations': LocationSerializer, 'asset_types': AssetTypeSerializer, 'resources': ResourceSerializer,
    'clusters': ClusterSerializer, 'teams': TeamSerializer, 'securityProviders': SecurityProviderSerializer,
    'products': ProductSerializer
    }

serializers_mapping_read = {
    'assets': AssetGetSerializer,
    'locations': LocationGetSerializer,
    'clusters': ClusterGetSerializer,
    'teams': TeamGetSerializer,
    'asset_types': AssetTypeSerializer,
    'products': ProductGetSerializer,
    'resources': ResourceGetSerializer,
    'securityProviders': SecurityProviderGetSerializer,
    'assetsEnvironments': AssetGetEnvironmentSerializer,
    'assetsUrls': AssetGetUrlSerializer,
}

serializers_mapping_associations = {

}

serializers_mapping_detail = {
    'assets': AssetGetDetailSerializer
}

serializer_class_lookup = CaseInsensitiveDict(serializers_mapping)
serializer_class_lookup_read = CaseInsensitiveDict(serializers_mapping_read)
serializer_class_lookup_associations = CaseInsensitiveDict(serializers_mapping_associations)
serializer_class_lookup_detail = CaseInsensitiveDict(serializers_mapping_detail)
