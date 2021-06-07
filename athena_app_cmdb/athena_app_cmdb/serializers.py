# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================
import pydash
import logging

from collections import OrderedDict
from django.utils import timezone
from rest_framework import serializers
from . import models
from copy import deepcopy
from requests.structures import CaseInsensitiveDict

logger = logging.getLogger(__name__)


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssetType
        fields = '__all__'


class AssetEnvironmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AssetEnvironment
        fields = '__all__'

    def to_internal_value(self, data):
        logger.info('ASSET ENV : {}'.format(data))
        if 'refid' not in data:
            data['refid'] = data['id']
            del data['id']
        return super(AssetEnvironmentSerializer, self).to_internal_value(data)


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
        if 'refid' not in data:
            data['refid'] = data['id']
            del data['id']
        if models.Team.objects.filter(refid=data['team']).exists():
            obj = models.Team.objects.get(refid=data['team'])
            data['team'] = obj.id
        if models.Product.objects.filter(refid=data['product']).exists():
            obj = models.Product.objects.get(refid=data['product'])
            data['product'] = obj.id
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

    def process_environments_data(self, data):
        key_list = []
        environments_data = OrderedDict()

        for key in data:
            if isinstance(data[key], list):
                for each in data[key]:
                    if 'environment' in each and 'entries' in each:
                        if key not in key_list:
                            key_list.append(key)
                        # processing environments data
                        env = each['environment']
                        entries = each['entries']
                        if key == 'aditionalUrls':
                            pydash.objects.set_(environments_data, '{}.{}'.format(env, key), each)
                        else:
                            pydash.objects.set_(environments_data, '{}.{}'.format(env, key), entries)
        if key_list:
            environments_data['key_list'] = key_list
        return environments_data

    def create(self, validated_data):
        properties = validated_data.pop('properties')
        environments_data = self.process_environments_data(properties)
        if 'key_list' in environments_data:
            for key in environments_data['key_list']:
                del properties[key]
        attaches = properties.pop('attaches', [])
        validated_data['properties'] = properties
        asset = models.Asset.objects.create(**validated_data)
        asset_id = asset.id
        for key in environments_data:
            if key != 'key_list':
                env = OrderedDict()
                env['id'] = key
                env['asset'] = asset_id
                env['properties'] = environments_data[key]
                if 'created_at' in validated_data:
                    env['created_at'] = validated_data.get('created_at',)
                if 'updated_at' in validated_data:
                    env['updated_at'] = validated_data.get('updated_at',)
                env['updated_by'] = validated_data.get('updated_by', "")
                env['created_by'] = validated_data.get('created_by', "")
                env['deleted'] = validated_data.get('deleted', 'f')
                item_serializer = AssetEnvironmentSerializer(data=env)
                if item_serializer.is_valid():
                    item_serializer.save()
                    item = item_serializer.data
                else:
                    errors = {'errors': ['Failed to save product environment data. ', item_serializer.errors]}
                    return errors
                # adding attaches
                attaches_list = []
                for resource in attaches.get('resources', []):
                    logger.info('ATTACHES {}'.format(resource))
                    if pydash.objects.get(resource, 'environments.0', '') == key:
                        if models.Resource.objects.filter(refid=resource.get('name', '')).exists():
                            robj = models.Resource.objects.get(
                                refid=resource.get('name', ''))
                            envobj = models.AssetEnvironment.objects.get(id=item['id'])
                            logger.info('ADDING')
                            robj.assetEnvironments.add(envobj)
                            attaches_list.append(resource.get('name'))
                # remove any attaches no longer
                cdata = models.Resource.objects.raw_all()
                pfiltername = 'assetEnvironments__id'
                logger.info('REF {}'.format(item))
                cfilter = {pfiltername: item['id']}
                cdata = cdata.filter(**cfilter)
                for each in cdata:
                    properties = each.properties
                    name = each.refid
                    robj = None
                    if name not in attaches_list:
                        robj = models.Resource.objects.get(refid=name)
                        robj.assetEnvironments.delete(item.id)
        return asset

    def update(self, instance, validated_data):
        properties = validated_data.pop('properties')
        environments_data = self.process_environments_data(properties)
        attaches = properties.pop('attaches', [])
        if 'key_list' in environments_data:
            for key in environments_data['key_list']:
                del properties[key]
        instance.refid = validated_data.get('refid', instance.refid)
        instance.properties = properties
        instance.deleted = validated_data.get('deleted', instance.deleted)
        instance.created_at = validated_data.get('created_at', instance.created_at)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.updated_at = validated_data.get('updated_at', timezone.now())
        instance.updated_by = validated_data.get('updated_by', instance.updated_by)
        instance.deleted_at = validated_data.get('deleted_at', instance.deleted_at)
        asset_id = instance.id
        for key in environments_data:
            if key != 'key_list':
                env = OrderedDict
                env['id'] = key
                env['asset'] = asset_id
                env['properties'] = environments_data[key]
                if 'created_at' in validated_data:
                    env['created_at'] = validated_data.get('created_at',)
                if 'updated_at' in validated_data:
                    env['updated_at'] = validated_data.get('updated_at',)
                env['updated_by'] = validated_data.get('updated_by', "")
                env['created_by'] = validated_data('created_by', "")
                env['deleted'] = validated_data('deleted', 'f')
                item_serializer = AssetEnvironmentSerializer(asset=instance, **env)
                if item_serializer.is_valid():
                    item_serializer.save()
                else:
                    errors = {'errors': ['Failed to save product environment data. ', item_serializer.errors]}
                    return errors
                envobj = None
                if models.AssetEnvironment.objects.filter(refid=env['id'], asset=asset_id).exists():
                    envobj = models.AssetEnvironment.objects.get(refid=env['id'], asset=asset_id)
                    env['id'] = str(envobj.values('id', flat=True))

                if envobj:
                    item_serializer = AssetEnvironmentSerializer(envobj, data=env)
                    if item_serializer.is_valid():
                        item_serializer.save()
                        item = item_serializer.data
                    else:
                        errors = {'errors': ['Failed to save product environment data. ', item_serializer.errors]}
                        return errors
                else:
                    item_serializer = AssetEnvironmentSerializer(data=env)
                    if item_serializer.is_valid():
                        item_serializer.save()
                        item = item_serializer.data
                    else:
                        errors = {'errors': ['Failed to save product environment data. ', item_serializer.errors]}
                        return errors
                # adding attaches
                attaches_list = []
                for resource in attaches.get('resources', []):
                    if pydash.objects.get(resource, 'environments.0', '') == key:
                        if models.Resource.objects.filter(properties__metadata__name=resource.get('name', '')).exists():
                            robj = models.Resource.objects.get(
                                properties__metadata__name=resource.get('name', ''))
                            robj.assetEnvironments.add(item.id)
                            attaches_list.append(resource.get('name'))
                # remove any attaches no longer
                resources = ResourceAssociationSerializer(item.resources, many=True).data
                for name in resources:
                    if name not in attaches_list:
                        robj = models.Resource.objects.get(properties__metadata__name=name)
                        robj.assetEnvironments.delete(item.id)
        instance.save()
        return instance


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
        if 'refid' not in data:
            data['refid'] = data['id']
            del data['id']
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
        if 'refid' not in data:
            data['refid'] = data['id']
            del data['id']
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


class ProductEnvironmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProductEnvironment
        fields = '__all__'

    def to_internal_value(self, data):
        if models.Location.objects.filter(refid=data['location']).exists():
            obj = models.Location.objects.get(refid=data['location'])
            data['location'] = obj.id
        data['refid'] = data['id']
        del data['id']
        return super(ProductEnvironmentSerializer, self).to_internal_value(data)


class ProductSerializer(serializers.ModelSerializer):
    attaches = serializers.JSONField(required=False)
    consumes = serializers.JSONField(required=False)
    internal = serializers.JSONField(required=False)
    security = serializers.JSONField(required=False)
    description = serializers.CharField(required=False)
    environments = serializers.JSONField(required=False)

    class Meta:
        model = models.Product
        fields = '__all__'

    def to_representation(self, instance):
        return ProductGetSerializer(instance).data

    def create(self, validated_data):
        environments = None
        if 'environments' in validated_data:
            environments = validated_data.pop('environments')
        product = models.Product.objects.create(**validated_data)
        if environments:
            for env in environments:
                if 'created_at' in validated_data:
                    env['created_at'] = validated_data.get('created_at',)
                if 'updated_at' in validated_data:
                    env['updated_at'] = validated_data.get('updated_at',)
                env['updated_by'] = validated_data.get('updated_by', "")
                env['created_by'] = validated_data.get('created_by', "")
                env['deleted'] = validated_data.get('deleted', 'f')
                prod_id = str(product.id)
                env['product'] = prod_id
                product_environment_serializer = ProductEnvironmentSerializer(product=product, **env)
                if product_environment_serializer.is_valid():
                    product_environment_serializer.save()
                else:
                    logger.error('Failed to save product environment data. '
                                 '{}'.format(product_environment_serializer.errors))
        return product

    def update(self, instance, validated_data):
        environments = None
        if 'environments' in validated_data:
            environments = validated_data.pop('environments')
        instance.refid = validated_data.get('refid', instance.refid)
        instance.properties = validated_data.get('properties', instance.properties)
        instance.deleted = validated_data.get('deleted', instance.deleted)
        instance.created_at = validated_data.get('created_at', instance.created_at)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.updated_at = validated_data.get('updated_at', timezone.now())
        instance.updated_by = validated_data.get('updated_by', instance.updated_by)
        instance.deleted_at = validated_data.get('deleted_at', instance.deleted_at)

        if environments:
            for env in environments:
                prod_id = str(instance.id)
                env['product'] = prod_id
                envobj = None
                if 'created_at' in validated_data:
                    env['created_at'] = validated_data.get('created_at')
                if 'updated_at' in validated_data:
                    env['updated_at'] = validated_data.get('updated_at')
                env['updated_by'] = validated_data.get('updated_by', "")
                env['created_by'] = validated_data.get('created_by', "")
                env['deleted'] = validated_data.get('deleted', 'f')
                if models.ProductEnvironment.objects.filter(refid=env['id'], product=instance.id).exists():
                    envobj = models.ProductEnvironment.objects.get(refid=env['id'], product=instance.id)
                    env['id'] = str(envobj.values('id', flat=True))
                if envobj:
                    product_environment_serializer = ProductEnvironmentSerializer(envobj, data=env)
                    if product_environment_serializer.is_valid():
                        product_environment_serializer.save()
                    else:
                        logger.error('Failed to save product environment data. '
                                     '{}'.format(product_environment_serializer.errors))
                else:
                    product_environment_serializer = ProductEnvironmentSerializer(data=env)
                    if product_environment_serializer.is_valid():
                        product_environment_serializer.save()
                    else:
                        logger.error('Failed to save product environment data. '
                                     '{}'.format(product_environment_serializer.errors))
        instance.save()
        return instance

    def to_internal_value(self, data):
        if 'refid' not in data:
            data['refid'] = data['id']
            del data['id']
        fields = [f.name for f in models.Product._meta.fields + models.Product._meta.many_to_many]
        properties = data.get('properties', {})
        data_copy = deepcopy(data)
        for key in data_copy:
            if key == 'env-type':
                key = 'env_type'
            if key not in fields and key != 'environments':
                properties[key] = data[key]
                del data[key]
        data['properties'] = properties
        return super(ProductSerializer, self).to_internal_value(data)


class ProductGetSerializer(serializers.ModelSerializer):
    environments = serializers.SlugRelatedField(many=True, slug_field='refid', read_only=True)
    id = serializers.ReadOnlyField(source='refid')

    class Meta:
        model = models.Product
        fields = ('id', 'properties', 'environments', 'deleted')

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
        spec = data.pop('spec')
        location_id = spec.pop('platform')
        owner_ref = spec.pop('owner')
        data['spec'] = spec
        if 'refid' not in data:
            metadata = data.pop('metadata')
            data['refid'] = metadata.pop('name')
            data['metadata'] = metadata
        if models.Location.objects.filter(refid=location_id).exists():
            locobj = models.Location.objects.get(refid=location_id)
            data['location'] = locobj.id
        if models.Team.objects.filter(refid=owner_ref).exists():
            teamobj = models.Team.objects.get(refid=owner_ref)
            data['owner'] = teamobj.id
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
    id = serializers.ReadOnlyField(source='refid')
    owner = serializers.ReadOnlyField(source='owner.refid')
    location = serializers.ReadOnlyField(source='location.refid')

    class Meta:
        model = models.Resource
        fields = ('id', 'owner', 'location', 'properties',
                  )

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks

    def to_representation(self, instance):
        data = super().to_representation(instance)
        properties = data.pop('properties', None)
        spec = properties.pop('spec')
        new_spec = OrderedDict()
        new_spec['type'] = spec.pop('type', {})
        new_spec['owner'] = data['owner']
        new_spec['platform'] = data['location']
        new_spec['definition'] = spec.pop('definition', {})
        new_spec['provisioner'] = spec.pop('provisioner', {})
        new_spec.update(spec)
        metadata = properties.pop('metadata')
        new_meta = OrderedDict()
        new_meta['name'] = data['id']
        new_meta['annotations'] = metadata.pop('annotations', {})
        new_meta['description'] = metadata.pop('description', '')
        new_meta.update(metadata)
        return_data = OrderedDict()
        return_data['spec'] = new_spec
        return_data['metadata'] = new_meta
        return_data.update(properties)
        return return_data


class ResourceAssociationSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='properties.metadata.name')


    class Meta:
        model = models.Resource
        fields = ('name', )


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Team
        fields = '__all__'

    def to_representation(self, instance):
        return TeamGetSerializer(instance).data

    def to_internal_value(self, data):
        if 'refid' not in data:
            data['refid'] = data['id']
            del data['id']
        fields = [f.name for f in models.Team._meta.fields + models.Team._meta.many_to_many]
        properties = data.get('properties', {})
        data_copy = deepcopy(data)
        for key in data_copy:
            if key not in fields:
                properties[key] = data[key]
                del data[key]
        data['properties'] = properties
        return super(TeamSerializer, self).to_internal_value(data)


class TeamGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='refid')

    class Meta:
        model = models.Team
        fields = ('id', 'name', 'properties', 'deleted',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        properties = data.pop('properties', None)
        data.update(properties)
        return data


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


class AssetEnvironmentAttachesSerializer(serializers.ModelSerializer):
    resources = serializers.SerializerMethodField()

    class Meta:
        model = models.AssetEnvironment
        fields = ('refid', 'resources', )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return_data = []
        for each in data.get('resources', []):
            tmp_data = {'name': str(each), 'environments': [data['refid'], ], }
            return_data.append(tmp_data)
        return return_data

    def get_resources(self, instance):
        robj = models.Resource.objects.values_list('refid', flat=True).filter(assetEnvironments__id=instance.id)
        return robj


class AssetGetSerializer(serializers.ModelSerializer):
    attaches = serializers.SerializerMethodField()

    class Meta:
        model = models.Asset
        fields = ('id', 'name', 'repo', 'team', 'type',
                  'product', 'attaches',
                  'appLanguage',  'assetMasterId', 'properties', 'deleted')

    def get_attaches(self, instance):
        aobj = models.AssetEnvironment.objects.filter(asset=instance.id)
        return AssetEnvironmentAttachesSerializer(aobj, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # get all the environments data
        tmp_data = OrderedDict()
        key_list = []
        asset_environments = models.AssetEnvironment.objects.filter(asset=instance.id)
        for env in asset_environments:
            env_properties = env.properties
            for item in env_properties:
                if item not in key_list:
                    key_list.append(item)
                    tmp_data[item] = []
                env_data = {'environment': env.refid, 'entries': env_properties[item]}
                tmp_data[item].append(env_data)
        data.update(tmp_data)
        properties = data.pop('properties', None)
        data.update(properties)
        return data

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks


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
