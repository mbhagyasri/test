import uuid
from django.db.models import Model, UUIDField, CharField, JSONField, ManyToManyField, ForeignKey, CASCADE

class Account(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=75)
    properties = JSONField()
    def __str__(self):
        return self.name  

class Location(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    account = ForeignKey(Account, on_delete=CASCADE)
    properties = JSONField()
    def __str__(self):
        return self.name

class Environment(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    location = ForeignKey(Location, on_delete=CASCADE)
    properties = JSONField()
    def __str__(self):
        return self.name

class Cluster(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    environment = ForeignKey(Environment, on_delete=CASCADE)
    properties = JSONField()
    def __str__(self):
        return self.name

class Team(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    properties = JSONField()
    def __str__(self):
        return self.name

class Product(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=50)
    environment = ForeignKey(Environment, on_delete=CASCADE)
    properties = JSONField()
    def __str__(self):
        return self.environment.name + "-" + self.name

class Egress(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=100)
    asset = ForeignKey(Asset, on_delete=CASCADE)
    properties = JSONField()
    def __str__(self):
        return self.asset.name + ":" + self.name

class Asset(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_id = CharField(max_length=100)  # svc-app-registry.
    name = CharField(max_length=100)
    environment = ForeignKey(Environment, on_delete=CASCADE)
    clusters = ManyToManyField(Cluster)
    team = ForeignKey(Team, on_delete=CASCADE)
    product = ForeignKey(Product, on_delete=CASCADE)
    securities =  ManyToManyField(Security)
    properties = JSONField()
    def __str__(self):
        return self.environment.name + "-" + self.asset_id

class Security(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=100)
    properties = JSONField()
    def __str__(self):
        return self.name

class Resource(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=100)
    properties = JSONField()
    def __str__(self):
        return self.name
