from django.contrib import admin
from django.contrib.postgres.fields import JSONField

from jsoneditor.admin import JSONFieldModelAdmin
from .models import Account, Location, Environment, Cluster, Team, Product, EgressRule, Asset, SecurityProvider, Resource, OnboardingRequest

# Register your models here.
admin.site.register([Account, Location, Environment, Cluster, Team, Product, EgressRule, Asset, SecurityProvider, Resource], JSONFieldModelAdmin, OnboardingRequest)