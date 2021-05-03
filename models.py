import uuid
from django.db.models import Model, UUIDField, CharField, JSONField, ManyToManyField, ForeignKey, UniqueConstraint, CASCADE

class Account(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=75)
    properties = JSONField(default=None)
    def __str__(self):
        return self.name 
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name'], name='unique_account_name')
        ]

class Location(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    account = ForeignKey(Account, on_delete=CASCADE)
    properties = JSONField(default=None)
    def __str__(self):
        return self.name
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name'], name='unique_location_name')
        ]

class Environment(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    location = ForeignKey(Location, on_delete=CASCADE)
    properties = JSONField(default=None)
    def __str__(self):
        return self.name
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name','location'], name='unique_environment_name')
        ]

class Cluster(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    environment = ForeignKey(Environment, on_delete=CASCADE)
    properties = JSONField(default=None)
    def __str__(self):
        return self.name
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name','environment'], name='unique_cluster_name')
        ]

class Team(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    properties = JSONField(default=None)
    def __str__(self):
        return self.name
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name'], name='unique_team_name')
        ]

class Product(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    environment = ForeignKey(Environment, on_delete=CASCADE)
    properties = JSONField(default=None)
    def __str__(self):
        return self.environment.name + "-" + self.name
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'environment'], name='unique_product_name')
        ]

class SecurityProvider(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=100)
    properties = JSONField(default=None)
    def __str__(self):
        return self.name
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name'], name='unique_security_name')
        ]

class Asset(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_id = CharField(max_length=100)  # svc-app-registry.
    name = CharField(max_length=100)
    environment = ForeignKey(Environment, on_delete=CASCADE)
    clusters = ManyToManyField(Cluster)
    team = ForeignKey(Team, on_delete=CASCADE)
    product = ForeignKey(Product, on_delete=CASCADE)
    securities =  ManyToManyField(SecurityProvider)
    properties = JSONField(default=None)
    def __str__(self):
        return self.environment.name + "-" + self.asset_id
    class Meta:
        constraints = [
            UniqueConstraint(fields=['asset_id', 'environment'], name='unique_asset_assetid'),
            UniqueConstraint(fields=['name', 'environment'], name='unique_asset_name')
        ]

class EgressRule(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=100)
    asset = ForeignKey(Asset, on_delete=CASCADE)
    properties = JSONField(default=None)
    def __str__(self):
        return self.asset.name + ":" + self.name
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'asset'], name='unique_egress_name')
        ]


class Resource(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=100)
    environment = ForeignKey(Environment, on_delete=CASCADE)
    properties = JSONField(default=None)
    def __str__(self):
        return self.name
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'environment'], name='unique_resource_name')
        ]
