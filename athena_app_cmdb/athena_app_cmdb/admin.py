# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global.
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================

import pydash
import logging
from django.contrib import admin
from django.utils.translation import gettext as _, gettext_lazy
from admin_auto_filters.filters import AutocompleteFilterFactory
from .ui import actions, filters

from . import forms
from . import models


logger = logging.getLogger(__name__)


class AppRegistryDefaultAdmin(admin.ModelAdmin):
    """
        Parent ModelAdmin that will be inherit by all the definition below.  Override these by setting individuals changes
        within the definition inside each of table definitions.
        Anything that should be global and applicable to all tables, should be set here
    """
    readonly_fields = ('created_at', 'updated_at', 'updated_by', 'created_by')
    list_display = ('id', 'name', )
    search_fields = ['name', 'id', 'properties']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user

        super(AppRegistryDefaultAdmin, self).save_model(request, obj, form, change)


# ---------------- Global Actions Section --------------------------------------------------------------------#
# Define the actions functions in the ui/actions.py
# Assign in this section for it to appears on all tables

# Override django built-in deleted method
admin.site.disable_action('delete_selected')


soft_delete_selected = actions.soft_delete_selected
soft_delete_selected.allowed_permissions = ('delete',)
soft_delete_selected.short_description = gettext_lazy("Delete selected %(verbose_name_plural)s")
admin.site.add_action(soft_delete_selected, 'soft_delete_selected')


# ------------------------ Individual Tables definitions goes here ---------------------------------------- #
# Register your models here.
# For each table, Add a <Tablename>Admin definition here and <TableName>Form in the forms.py file


@admin.register(models.Location)
class LocationAdmin(AppRegistryDefaultAdmin):
    form = forms.LocationForm
    list_display = ('id', 'name', 'description', 'aws_account_id')

    def aws_account_id(self, obj):
        return pydash.objects.get(obj, 'properties.parameters.integration.aws.id', '')

    def description(self, obj):
        return obj.properties.get('description', '')


@admin.register(models.Cluster)
class ClusterAdmin(AppRegistryDefaultAdmin):
    form = forms.ClusterForm
    autocomplete_fields = ['location', ]
    list_display = ('id', 'name', 'location', 'uri')

    def uri(self, obj):
        return obj.properties.get('uri', '')


@admin.register(models.Team)
class TeamAdmin(AppRegistryDefaultAdmin):
    form = forms.TeamForm
    list_display = ('id', 'name', 'notification')

    def notification(self, obj):
        if obj.properties:
            return obj.properties.get('notification', '')


@admin.register(models.Product)
class ProductAdmin(AppRegistryDefaultAdmin):
    form = forms.ProductForm
    list_display = ('id', 'name', 'location')


@admin.register(models.Asset)
class AssetAdmin(AppRegistryDefaultAdmin):
    form = forms.AssetForm
    list_display = ('id', 'name', )


@admin.register(models.Resource)
class ResourceAdmin(AppRegistryDefaultAdmin):
    form = forms.TeamForm
    list_display = ('id', 'name', 'type', 'location')

    def type(self, obj):
        if obj.properties:
            return obj.properties.get('spec.type', '')
