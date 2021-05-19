# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================
import pydash
import logging

from django.utils import timezone

from rest_framework import serializers
from . import models
from requests.structures import CaseInsensitiveDict

logger = logging.getLogger(__name__)
athena_app_cmdb_API_PATH = '/api/athena_app_cmdb'


class LocationSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(required=False)
    region = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    parameters = serializers.JSONField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = models.Location
        fields = '__all__'

    def to_representation(self, instance):
        return LocationGetSerializer(instance).data

    def process_validated_data(self, properties, validated_data):
        logger.info(validated_data)
        if 'domain' in validated_data:
            properties['domain'] = validated_data.get('domain')
        if 'region' in validated_data:
            properties['region'] = validated_data.get('region')
        if 'status' in validated_data:
            properties['status'] = validated_data.get('status')
        if 'parameters' in validated_data:
            properties['parameters'] = validated_data.get('parameters')
        if 'description' in validated_data:
            properties['description'] = validated_data.get('description')
        return properties

    def create(self, validated_data):
        properties = validated_data.get('properties', {})
        # backward compatible to app registry v1
        properties = self.process_validated_data(properties, validated_data)
        validated_data['properties'] = properties
        resource = models.Location.objects.create(**validated_data)
        return resource

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        properties = validated_data.get('properties', instance.properties)
        instance.deleted = validated_data.get('deleted', instance.deleted)
        instance.created_at = validated_data.get('created_at', instance.created_at)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.updated_at = validated_data.get('updated_at', timezone.now())
        instance.updated_by = validated_data.get('updated_by', instance.updated_by)
        instance.deleted_at = validated_data.get('deleted_at', instance.deleted_at)
        logger.info('----')
        logger.info('BEFORE')
        logger.info(properties)
        properties = self.process_validated_data(properties, validated_data)
        logger.info('------')
        logger.info('AFTER')
        logger.info(properties)
        instance.properties = properties
        instance.save()
        return instance


class LocationGetSerializer(serializers.ModelSerializer):
    domain = serializers.ReadOnlyField(source='properties.domain', required=False)
    region = serializers.ReadOnlyField(source='properties.region', required=False)
    status = serializers.ReadOnlyField(source='properties.status', required=False)
    parameters = serializers.ReadOnlyField(source='properties.parameters', required=False)
    environment_name = serializers.ReadOnlyField(source='environment.name', required=False)
    description = serializers.ReadOnlyField(source='properties.description', required=False)
    links = serializers.SerializerMethodField()

    class Meta:
        model = models.Location
        fields = ('id', 'name', 'domain', 'region', 'status',
                  'environment_name', 'parameters',
                  'description', 'properties',
                  'links', 'updated_at', 'updated_by',
                  'created_at', 'created_by', 'deleted',)

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks




class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cluster
        fields = '__all__'

    def to_representation(self, instance):
        return ClusterGetSerializer(instance).data


class ClusterGetSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()
    uri = serializers.ReadOnlyField(source='properties.uri', required=False)

    class Meta:
        model = models.Cluster
        fields = ('id', 'name', 'uri', 'properties',
                  'links', 'updated_at', 'updated_by',
                  'created_at', 'created_by', 'deleted',)

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks


class TeamSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    notification = serializers.ListField(required=False)

    class Meta:
        model = models.Team
        fields = '__all__'

    def to_representation(self, instance):
        return TeamGetSerializer(instance).data

    def process_validated_data(self, properties, validated_data):
        if 'ad-group' in validated_data:
            properties['ad-group'] = validated_data.get('ad-group')
        if 'description' in validated_data:
            properties['description'] = validated_data.get('description')
        if 'notification' in validated_data:
            properties['notification'] = validated_data.get('notification')
        if 'email' in validated_data:
            properties['email'] = validated_data.get('email')
        return properties

    def create(self, validated_data):
        properties = validated_data.get('properties', {})
        # backward compatible to app registry v1
        properties = self.process_validated_data(properties, validated_data)
        validated_data['properties'] = properties
        team = models.Team.objects.create(**validated_data)
        return team


def update(self, instance, validated_data):
    instance.name = validated_data.get('name', instance.name)
    properties = validated_data.get('properties', instance.properties)
    instance.deleted = validated_data.get('deleted', instance.deleted)
    instance.created_at = validated_data.get('created_at', instance.created_at)
    instance.created_by = validated_data.get('created_by', instance.created_by)
    instance.updated_at = validated_data.get('updated_at', timezone.now())
    instance.updated_by = validated_data.get('updated_by', instance.updated_by)
    instance.deleted_at = validated_data.get('deleted_at', instance.deleted_at)
    properties = self.process_validated_data(properties, validated_data)
    instance.properties = properties
    instance.save()
    return instance


class TeamGetSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source='properties.email', required=False)
    description = serializers.ReadOnlyField(source='properties.description', required=False)
    notification = serializers.ReadOnlyField(source='properties.notification', required=False)

    class Meta:
        model = models.Team
        fields = ('id', 'name',
                  'email', 'description', 'notification', 'properties',
                  'links', 'updated_at', 'updated_by',
                  'created_at', 'created_by', 'deleted',)

    def get_links(self, instance):
        lks = {'_self': instance.self_links}
        return lks

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if pydash.objects.has(data, 'properties.ad-group'):
            data['ad-group'] = pydash.objects.get(data, 'properties.ad-group', None)
        return data


class AssetType(serializers.ModelSerializer):
    class Meta:
        model = models.AssetType
        fields = '__all__'

serializers_mapping = {'locations': LocationSerializer, 'asset_types': AssetType,
                       'clusters': ClusterSerializer, 'teams': TeamSerializer
                       }

serializers_mapping_read = {
    'locations': LocationGetSerializer,
    'clusters': ClusterGetSerializer,
    'teams': TeamGetSerializer,
    'asset_types': AssetType
}

serializers_mapping_associations = {

}

serializers_mapping_detail = {

}

serializer_class_lookup = CaseInsensitiveDict(serializers_mapping)
serializer_class_lookup_read = CaseInsensitiveDict(serializers_mapping_read)
serializer_class_lookup_associations = CaseInsensitiveDict(serializers_mapping_associations)
serializer_class_lookup_detail = CaseInsensitiveDict(serializers_mapping_detail)
