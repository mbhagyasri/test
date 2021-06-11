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
from .middleware import ViewException

logger = logging.getLogger(__name__)
FORMAT = 'json'


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssetType
        fields = '__all__'


class AssetEnvironmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AssetEnvironment
        fields = '__all__'

    def to_internal_value(self, data):
        if 'refid' not in data:
            data['refid'] = data['id']
            del data['id']
        return super(AssetEnvironmentSerializer, self).to_internal_value(data)


class AssetByEnvironmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AssetEnvironment
        fields = '__all_all'

    def to_internal_value(self, data):
        if 'refid' not in data:
            data['refid'] = data['id']
            del data['id']
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
        return super(AssetByEnvironmentSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        return AssetByEnvironmentGetSerializer(instance.data)



class AssetGetDetailSerializer(serializers.ModelSerializer):
    attaches = serializers.SerializerMethodField()

    class Meta:
        model = models.Asset
        fields = ('id', 'refid', 'name', 'repo', 'team', 'type',
                  'product', 'attaches',
                  'appLanguage',  'assetMasterId', 'properties', 'deleted')

    def get_attaches(self, instance):
        aobj = models.AssetEnvironment.objects.filter(asset=instance.id)
        data = AssetEnvironmentAttachesSerializer(aobj, many=True).data
        return_data = []
        for each in data:
            if each:
                return_data.append(each)
        return return_data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # get all the environments data
        tmp_data = OrderedDict()
        key_list = []
        attaches = data.pop('attaches')
        resources = []
        for each in attaches:
            for item in each:
                if item:
                    resources.append(item)
        if resources:
            data.update({"attaches": {"resources": resources}})
        properties = data.pop('properties', None)
        data.update(properties)
        return data

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks


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
        environments_data = {}
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
        product = ProductGetDetailSerializer(asset.product).data
        try:
            for key in product['environments']:
                env_id = key['refid']
                envobj = None
                env = OrderedDict()
                env['refid'] = env_id
                env['product_environment'] = models.ProductEnvironment.objects.get(id=key['id'])
                if env_id in environments_data:
                    env['properties'] = environments_data[env_id]
                if 'created_at' in validated_data:
                    env['created_at'] = validated_data.get('created_at', )
                if 'updated_at' in validated_data:
                    env['updated_at'] = validated_data.get('updated_at', )
                env['updated_by'] = validated_data.get('updated_by', "")
                env['created_by'] = validated_data.get('created_by', "")
                env['deleted'] = validated_data.get('deleted', 'f')
                env['asset'] = asset
                envobj = models.AssetEnvironment.objects.create(**env)

                # adding attaches
                attaches_list = []
                if attaches:
                    for resource in attaches.get('resources', []):
                        robj = None
                        if pydash.objects.get(resource, 'environments.0', '') == env_id:
                            logger.info(
                                pydash.objects.get(resource, 'environments.0', 'NOT FOUND') + 'key {}'.format(key))
                            if models.Resource.objects.filter(refid=resource.get('name', '')).exists():
                                robj = models.Resource.objects.get(
                                    refid=resource.get('name', ''))
                                robj.assetEnvironments.add(envobj)
                                attaches_list.append(resource.get('name'))
                # remove any attaches no longer
                cdata = models.Resource.objects.raw_all()
                pfiltername = 'assetEnvironments__id'
                cfilter = {pfiltername: envobj.id}
                cdata = cdata.filter(**cfilter)
                for each in cdata:
                    properties = each.properties
                    name = each.refid
                    robj = None
                    if name not in attaches_list:
                        robj = models.Resource.objects.get(refid=name)
                        robj.assetEnvironments.delete(envobj)
        except Exception as e:
            logger.exception(e)
            #roll back creation
            asset.hard_delete()
            raise ViewException(FORMAT, 'Invalid Request', 400)
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
        product = ProductGetSerializer(instance.product).data
        asset_id = instance.id
        try:
            for key in product['environments']:
                env_id = key['id']
                logger.info('PROCESSING ENV {}'.format(env_id))
                envobj = None
                env = OrderedDict()
                env['refid'] = env_id
                if env_id in environments_data:
                    env['properties'] = environments_data[env_id]
                if 'created_at' in validated_data:
                    env['created_at'] = validated_data.get('created_at', )
                if 'updated_at' in validated_data:
                    env['updated_at'] = validated_data.get('updated_at', )
                env['updated_by'] = validated_data.get('updated_by', "")
                env['created_by'] = validated_data.get('created_by', "")
                env['deleted'] = validated_data.get('deleted', 'f')
                env['asset'] = instance
                if models.AssetEnvironment.objects.filter(refid=env_id, asset=asset_id).exists():
                    envobj = models.AssetEnvironment.objects.get(refid=env_id, asset=asset_id)
                if envobj:
                    envobj.properties = env.get('properties', envobj.properties)
                    envobj.updated_by = env.get('updated_by', envobj.updated_by)
                    envobj.deleted = env.get('deleted', envobj.deleted)
                    envobj.created_by = env.get('created_by', envobj.created_by)
                    envobj.updated_at = env.get('updated_at', envobj.updated_at)
                    envobj.created_at = env.get('created_at', envobj.created_at)
                    envobj.save()
                else:
                    envobj = models.AssetEnvironment.objects.create(**env)
                # adding attaches
                attaches_list = []
                logger.info('PROCESSING {}'.format(env_id))
                for resource in attaches.get('resources', []):
                    robj = None
                    name = resource['name']
                    envs = resource['environments']
                    env_resource = envs[0]
                    logger.info('NAME {}, env[0] {}'.format(name, env_resource))
                    if str(env_resource) == str(env_id):
                        logger.info('found match')
                        if models.Resource.objects.filter(refid=resource.get('name', '')).exists():
                            logger.info('WE FOUND IT')
                            robj = models.Resource.objects.get(
                                refid=resource.get('name', ''))
                            logger.info('ADDING')
                            robj.assetEnvironments.add(envobj)
                            attaches_list.append(resource.get('name'))
                # remove any attaches no longer
                #cdata = models.Resource.objects.raw_all()
                #pfiltername = 'assetEnvironments__id'
                #cfilter = {pfiltername: envobj.id}
                #cdata = cdata.filter(**cfilter)
                #for each in cdata:
                #    properties = each.properties
                #    name = each.refid
                #    robj = None
                #    if name not in attaches_list:
                #        robj = models.Resource.objects.get(refid=name)
                #        robj.assetEnvironments.delete(envobj)
        except Exception as e:
            logger.exception(e)
            raise ViewException(FORMAT, 'Invalid Request', 400)
        instance.save()
        return instance


class AssetGetEnvironmentSerializer(serializers.ModelSerializer):
    environments = serializers.SerializerMethodField()


    class Meta:
        model = models.Asset
        fields = ('id', 'environments', 'product')

    def get_environments(self, instance):
        product = ProductGetSerializer(instance.product).data
        data = product.get('environments', [])
        return data


class AssetGetUrlSerializer(serializers.ModelSerializer):
    locations = serializers.SerializerMethodField()
    environments = serializers.SerializerMethodField()
    additionalUrls = serializers.SerializerMethodField()

    class Meta:
        model = models.Asset
        fields = ('id', 'name', 'environments', 'locations', 'properties', 'type', 'product', 'additionalUrls')

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
                if models.Location.objects.filter(refid=env.get('location')).exists():
                    loc = models.Location.objects.get(refid=env.get('location'))
                    location = LocationGetSerializer(loc).data
                    data.append(location)
        return data

    def get_additionalUrls(self, instance):
        asset_environments = models.AssetEnvironment.objects.filter(asset=instance.id)
        return_data = []
        for env in asset_environments:
            env_properties = env.properties
            if 'additionalUrls' in env_properties:
                env_data = {'environment': env.refid, 'entries': env_properties['additionalUrls']}
                return_data.append(env_data)
        return return_data

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
            if 'additionalUrls' in data and data.get('additionalUrls', []) != []:
                for url in pydash.objects.get(data, 'additionalUrls', []):
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
    id = serializers.ReadOnlyField(source='refid')

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
    id = serializers.ReadOnlyField(source='refid')

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


class ProductEnvironmentGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='refid')
    location = serializers.ReadOnlyField(source='location.refid')
    class Meta:
        model = models.ProductEnvironment
        fields = ('id', 'type', 'prefix', 'location')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        copy_data = deepcopy(data)
        for each in copy_data:
            if not copy_data.get(each, None):
                del data[each]
        return data


class ProductEnvironmentGetDetailSerializer(serializers.ModelSerializer):
    """ Use this serializer to get full data and normal UUID info"""
    location = serializers.ReadOnlyField(source='location.refid')

    class Meta:
        model = models.ProductEnvironment
        fields = ('id', 'refid', 'type', 'prefix', 'location')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        copy_data = deepcopy(data)
        for each in copy_data:
            if not copy_data.get(each, None):
                del data[each]
        return data


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
        prod_id = str(product.id)
        if environments:
            for env in environments:
                if models.Location.objects.filter(refid=env['location']).exists():
                    loc = models.Location.objects.get(refid=env['location'])
                    env['location'] = loc
                if models.EnvType.objects.filter(id=env['type']).exists():
                    type = models.EnvType.objects.get(id=env['type'])
                    env['type'] = type
                if 'created_at' in validated_data:
                    env['created_at'] = validated_data.get('created_at',)
                if 'updated_at' in validated_data:
                    env['updated_at'] = validated_data.get('updated_at',)
                env['updated_by'] = validated_data.get('updated_by', "")
                env['created_by'] = validated_data.get('created_by', "")
                env['deleted'] = validated_data.get('deleted', 'f')
                env['product'] = product
                env['refid'] = env.pop('id')
                models.ProductEnvironment.objects.create(**env)
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
        prod_id = str(instance.id)
        if environments:
            for env in environments:

                env['product'] = instance
                envobj = None
                if 'created_at' in validated_data:
                    env['created_at'] = validated_data.get('created_at')
                if 'updated_at' in validated_data:
                    env['updated_at'] = validated_data.get('updated_at')
                env['updated_by'] = validated_data.get('updated_by', "")
                env['created_by'] = validated_data.get('created_by', "")
                env['deleted'] = validated_data.get('deleted', 'f')
                env['refid'] = env.pop('id')
                if models.Location.objects.filter(refid=env['location']).exists():
                    loc = models.Location.objects.get(refid=env['location'])
                    env['location'] = loc
                if models.EnvType.objects.filter(id=env['type']).exists():
                    type = models.EnvType.objects.get(id=env['type'])
                    env['type'] = type
                if models.ProductEnvironment.objects.filter(refid=env['refid'], product=instance.id).exists():
                    envobj = models.ProductEnvironment.objects.get(refid=env['refid'], product=instance.id)
                if envobj:
                    envobj.type = env.get('type', envobj.type)
                    envobj.prefix = env.get('prefix', envobj.prefix)
                    envobj.location = env.get('location', envobj.location)
                    envobj.updated_by = env.get('updated_by', envobj.updated_by)
                    envobj.deleted = env.get('deleted', envobj.deleted)
                    envobj.created_by = env.get('created_by', envobj.created_by)
                    envobj.updated_at = env.get('updated_at', envobj.updated_at)
                    envobj.created_at = env.get('created_at', envobj.created_at)
                    envobj.save()
                else:
                    models.ProductEnvironment.objects.create(**env)
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

class ProductGetDetailSerializer(serializers.ModelSerializer):
    environments = ProductEnvironmentGetDetailSerializer(many=True, read_only=True)

    class Meta:
        model = models.Product
        fields = ('id', 'refid', 'properties', 'environments', 'deleted')


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

class ProductGetSerializer(serializers.ModelSerializer):
    environments = ProductEnvironmentGetSerializer(many=True, read_only=True)
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
            if not each:
                continue
            tmp_data = {'name': str(each), 'environments': [data['refid'], ], }
            return_data.append(tmp_data)
        return return_data

    def get_resources(self, instance):
        robj = models.Resource.objects.values_list('refid', flat=True).filter(assetEnvironments__id=instance.id)
        return robj


class AssetByEnvironmentGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='refid')
    asset = AssetGetDetailSerializer()
    attaches = AssetEnvironmentAttachesSerializer(required=False)

    class Meta:
        model = models.AssetEnvironment
        fields = ('id', 'asset', 'properties')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        asset = data.pop('asset')
        return_data = OrderedDict()
        return_data['id'] = asset['refid']
        return_data['environment'] = data['id']
        del asset['id']
        del asset['refid']
        if 'attaches' in asset:
            del asset['attaches']
        return_data.update(asset)
        del data['id']
        return_data['attaches'] = data['attaches']
        properties = data.pop('properties', None)
        return_data.update(properties)
        return return_data


class AssetGetSerializer(serializers.ModelSerializer):
    attaches = serializers.SerializerMethodField()

    class Meta:
        model = models.Asset
        fields = ('id', 'refid', 'name', 'repo', 'team', 'type',
                  'product', 'attaches',
                  'appLanguage',  'assetMasterId', 'properties', 'deleted')

    def get_attaches(self, instance):
        aobj = models.AssetEnvironment.objects.filter(asset=instance.id)
        data = AssetEnvironmentAttachesSerializer(aobj, many=True).data
        return_data = []
        for each in data:
            if each:
                return_data.append(each)
        return return_data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = data['refid']
        del data['refid']
        # get all the environments data
        tmp_data = OrderedDict()
        key_list = []
        attaches = data.pop('attaches')
        resources = []
        for each in attaches:
            for item in each:
                if item:
                    resources.append(item)
        if resources:
            data.update({"attaches": {"resources": resources}})
        asset_environments = models.AssetEnvironment.objects.filter(asset=instance.id)
        if asset_environments:
            for env in asset_environments:
                env_properties = env.properties

                if env_properties:
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
    'products': ProductSerializer, 'assetsByEnvironment': AssetByEnvironmentSerializer
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
    'assetsByEnvironment': AssetByEnvironmentGetSerializer,
}

serializers_mapping_associations = {

}

serializers_mapping_detail = {
    'assets': AssetGetDetailSerializer,
    'products': ProductGetDetailSerializer
}

serializer_class_lookup = CaseInsensitiveDict(serializers_mapping)
serializer_class_lookup_read = CaseInsensitiveDict(serializers_mapping_read)
serializer_class_lookup_associations = CaseInsensitiveDict(serializers_mapping_associations)
serializer_class_lookup_detail = CaseInsensitiveDict(serializers_mapping_detail)
