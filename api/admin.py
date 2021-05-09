from django.contrib import admin
from .models import Account, Location, Environment, Cluster, Team, Product, EgressRule, Asset, SecurityProvider, Resource

# Register your models here.
admin.site.register([Account, Location, Environment, Cluster, Team, Product, EgressRule, Asset, SecurityProvider, Resource])
