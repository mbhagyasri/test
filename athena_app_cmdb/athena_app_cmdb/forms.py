# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global.
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================

import datetime
import logging
from django import forms
from django_currentuser.middleware import get_current_authenticated_user
from django_json_widget.widgets import JSONEditorWidget
from . import models


logger = logging.getLogger(__name__)


class AppRegistryForm(forms.ModelForm):
    created_at = forms.DateTimeField(initial=datetime.datetime.utcnow())
    updated_at = forms.DateTimeField(initial=datetime.datetime.utcnow())


    class Meta:
        abstract = True
        widgets = {
            'properties': JSONEditorWidget(width='800px', height='800px')

        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        self.db_name = ''
        if instance:
            self.db_name = instance._meta.db_table
        super(AppRegistryForm, self).__init__(*args, **kwargs)


    def clean(self):
        self.cleaned_data['updated_at'] = datetime.datetime.utcnow()
        self.cleaned_data['updated_by'] = str(get_current_authenticated_user())
        return self.cleaned_data

# ----------------------------------- Add Each Table fields definition below --------------------------- #


class EnvironmentForm(AppRegistryForm):

    class Meta:
        model = models.Environment
        exclude = ['deleted', 'deleted_at', 'original_name']
        widgets = {
            'properties': JSONEditorWidget(width='800px', height='800px')

        }


class LocationForm(AppRegistryForm):

    class Meta:
        model = models.Location
        exclude = ['deleted', 'deleted_at', 'original_name']
        widgets = {
            'properties': JSONEditorWidget(width='800px', height='800px')

        }


class ClusterForm(AppRegistryForm):

    class Meta:
        model = models.Cluster
        exclude = ['deleted', 'deleted_at', 'original_name']
        widgets = {
            'properties': JSONEditorWidget(width='800px', height='800px')

        }


class TeamForm(AppRegistryForm):

    class Meta:
        model = models.Team
        exclude = ['deleted', 'deleted_at', 'original_name']
        widgets = {
            'properties': JSONEditorWidget(width='800px', height='800px')

        }

class ProductForm(AppRegistryForm):

    class Meta:
        model = models.Product
        exclude = ['deleted', 'deleted_at', 'original_name']
        widgets = {
            'properties': JSONEditorWidget(width='800px', height='800px')

        }

class AssetForm(AppRegistryForm):

    class Meta:
        model = models.Asset
        exclude = ['deleted', 'deleted_at', 'original_name']
        widgets = {
            'properties': JSONEditorWidget(width='800px', height='800px')

        }

class ResourceForm(AppRegistryForm):

    class Meta:
        model = models.Resource
        exclude = ['deleted', 'deleted_at', 'original_name']
        widgets = {
            'properties': JSONEditorWidget(width='800px', height='800px')

        }