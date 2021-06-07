# Generated by Django 3.2.3 on 2021-06-07 13:02

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppLanguage',
            fields=[
                ('id', models.CharField(db_column='id', max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'App Language',
                'db_table': 'app_language',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, db_column='deleted_at', null=True)),
                ('original_id', models.CharField(blank=True, db_column='original_id', max_length=255, null=True)),
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('refid', models.CharField(db_column='asset_id', max_length=100, unique=True)),
                ('name', models.CharField(db_column='app_name', max_length=255)),
                ('repo', models.CharField(db_column='repo', max_length=200)),
                ('assetMasterId', models.IntegerField(blank=True, db_column='asset_master_id', null=True)),
                ('properties', models.JSONField(blank=True, db_column='json', null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
                ('appLanguage', models.ForeignKey(blank=True, db_column='app_language_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='athena_app_cmdb.applanguage')),
            ],
            options={
                'verbose_name': 'Asset',
                'db_table': 'asset',
                'ordering': ['-updated_at', '-created_at'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AssetEnvironment',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, db_column='deleted_at', null=True)),
                ('original_id', models.CharField(blank=True, db_column='original_id', max_length=255, null=True)),
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('refid', models.CharField(db_column='assetEnvironment_id', max_length=100)),
                ('properties', models.JSONField(blank=True, db_column='json', null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='environments', to='athena_app_cmdb.asset')),
            ],
            options={
                'verbose_name': 'Environment',
                'db_table': 'asset_environment',
                'managed': True,
                'unique_together': {('refid', 'asset')},
            },
        ),
        migrations.CreateModel(
            name='AssetType',
            fields=[
                ('id', models.CharField(db_column='id', max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', max_length=100)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
            ],
            options={
                'db_table': 'asset_type',
            },
        ),
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, db_column='deleted_at', null=True)),
                ('original_id', models.CharField(blank=True, db_column='original_id', max_length=255, null=True)),
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('refid', models.CharField(db_column='cluster_id', max_length=100, unique=True)),
                ('uri', models.CharField(db_column='uri', max_length=100)),
                ('properties', models.JSONField(blank=True, db_column='json', null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Kubernetes Cluster',
                'db_table': 'cluster',
                'ordering': ['-updated_at', '-created_at'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DatabaseChangeLog',
            fields=[
                ('id', models.CharField(db_column='id', max_length=255, primary_key=True, serialize=False)),
                ('author', models.CharField(db_column='author', max_length=255)),
                ('filename', models.CharField(max_length=255)),
                ('dateexecuted', models.DateTimeField(auto_now_add=True, db_column='dateexecuted')),
                ('orderexecuted', models.IntegerField(db_column='orderexecuted')),
                ('exectype', models.CharField(db_column='exectype', max_length=10)),
                ('md5sum', models.CharField(blank=True, db_column='md5sum', max_length=35, null=True)),
                ('description', models.CharField(blank=True, db_column='description', max_length=255, null=True)),
                ('comments', models.CharField(blank=True, db_column='comments', max_length=255, null=True)),
                ('tag', models.CharField(blank=True, db_column='tag', max_length=255, null=True)),
                ('liquibase', models.CharField(blank=True, db_column='liquibase', max_length=20, null=True)),
                ('contexts', models.CharField(blank=True, db_column='contexts', max_length=255, null=True)),
                ('labels', models.CharField(blank=True, db_column='labels', max_length=255, null=True)),
                ('deployment_id', models.CharField(blank=True, db_column='deployment_id', max_length=10, null=True)),
            ],
            options={
                'verbose_name': 'Database Change Log',
                'db_table': 'databasechangelog',
            },
        ),
        migrations.CreateModel(
            name='DatabaseChangeLogLock',
            fields=[
                ('id', models.IntegerField(db_column='id', primary_key=True, serialize=False)),
                ('locked', models.BooleanField(db_column='locked')),
                ('lockgranted', models.DateTimeField(blank=True, db_column='lockgranted', null=True)),
                ('lockedby', models.CharField(blank=True, db_column='lockedby', max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Database Change Log Lock',
                'db_table': 'databasechangeloglock',
            },
        ),
        migrations.CreateModel(
            name='EnvType',
            fields=[
                ('id', models.CharField(db_column='id', max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', max_length=50)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Environment Type',
                'db_table': 'env_type',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, db_column='deleted_at', null=True)),
                ('original_id', models.CharField(blank=True, db_column='original_id', max_length=255, null=True)),
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('refid', models.CharField(db_column='location_id', max_length=100, unique=True)),
                ('name', models.CharField(db_column='name', max_length=100, unique=True)),
                ('domain', models.CharField(db_column='domain', max_length=100)),
                ('properties', models.JSONField(blank=True, db_column='json', null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('env_type', models.ForeignKey(blank=True, db_column='env_type_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='athena_app_cmdb.envtype')),
            ],
            options={
                'verbose_name': 'Location',
                'db_table': 'location',
                'ordering': ['-updated_at', '-created_at'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='LocationRegion',
            fields=[
                ('id', models.CharField(db_column='id', max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', max_length=50)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Location Region',
                'db_table': 'location_region',
            },
        ),
        migrations.CreateModel(
            name='LocationStatus',
            fields=[
                ('id', models.CharField(db_column='id', max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', max_length=50)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Location Status',
                'db_table': 'location_status',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, db_column='deleted_at', null=True)),
                ('original_id', models.CharField(blank=True, db_column='original_id', max_length=255, null=True)),
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('refid', models.CharField(db_column='product_id', max_length=100, unique=True)),
                ('properties', models.JSONField(blank=True, db_column='json', null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Product',
                'db_table': 'product',
                'ordering': ['-updated_at', '-created_at'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SecurityProvider',
            fields=[
                ('id', models.CharField(db_column='id', max_length=100, primary_key=True, serialize=False)),
                ('schemes', models.CharField(db_column='schemes', max_length=30)),
                ('properties', models.JSONField(blank=True, db_column='json', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Security Provider',
                'db_table': 'securityprovider',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, db_column='deleted_at', null=True)),
                ('original_id', models.CharField(blank=True, db_column='original_id', max_length=255, null=True)),
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('refid', models.CharField(db_column='team_id', max_length=100, unique=True)),
                ('name', models.CharField(db_column='name', max_length=100, unique=True)),
                ('properties', models.JSONField(blank=True, db_column='json', null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Team',
                'db_table': 'team',
                'ordering': ['-updated_at', '-created_at'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, db_column='deleted_at', null=True)),
                ('original_id', models.CharField(blank=True, db_column='original_id', max_length=255, null=True)),
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('refid', models.CharField(db_column='resource_id', max_length=100, unique=True)),
                ('properties', models.JSONField(blank=True, db_column='json', null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
                ('assetEnvironments', models.ManyToManyField(blank=True, related_name='resources', to='athena_app_cmdb.AssetEnvironment')),
                ('location', models.ForeignKey(blank=True, db_column='location', null=True, on_delete=django.db.models.deletion.SET_NULL, to='athena_app_cmdb.location')),
                ('owner', models.ForeignKey(blank=True, db_column='owner', null=True, on_delete=django.db.models.deletion.SET_NULL, to='athena_app_cmdb.team')),
            ],
            options={
                'verbose_name': 'Resource',
                'db_table': 'resource',
                'ordering': ['-updated_at', '-created_at'],
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='location',
            name='region',
            field=models.ForeignKey(blank=True, db_column='region', null=True, on_delete=django.db.models.deletion.SET_NULL, to='athena_app_cmdb.locationregion'),
        ),
        migrations.AddField(
            model_name='location',
            name='status',
            field=models.ForeignKey(blank=True, db_column='status', null=True, on_delete=django.db.models.deletion.SET_NULL, to='athena_app_cmdb.locationstatus'),
        ),
        migrations.CreateModel(
            name='AssetBackup',
            fields=[
                ('id', models.CharField(db_column='id', max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='app_name', max_length=255, unique=True)),
                ('properties', models.JSONField(blank=True, db_column='json', null=True)),
                ('repo', models.CharField(blank=True, db_column='repo', max_length=200, null=True)),
                ('assetMasterId', models.IntegerField(db_column='asset_master_id')),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
                ('appLanguage', models.ForeignKey(db_column='app_language_id', on_delete=django.db.models.deletion.CASCADE, to='athena_app_cmdb.applanguage')),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, to='athena_app_cmdb.product')),
                ('team', models.ForeignKey(db_column='team_id', on_delete=django.db.models.deletion.CASCADE, to='athena_app_cmdb.team')),
                ('type', models.ForeignKey(db_column='asset_type_id', on_delete=django.db.models.deletion.CASCADE, to='athena_app_cmdb.assettype')),
            ],
            options={
                'verbose_name': 'Asset Backup',
                'db_table': 'asset_backup',
                'ordering': ['-updated_at', '-created_at'],
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='asset',
            name='product',
            field=models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, to='athena_app_cmdb.product'),
        ),
        migrations.AddField(
            model_name='asset',
            name='team',
            field=models.ForeignKey(db_column='team_id', on_delete=django.db.models.deletion.CASCADE, to='athena_app_cmdb.team'),
        ),
        migrations.AddField(
            model_name='asset',
            name='type',
            field=models.ForeignKey(db_column='asset_type_id', on_delete=django.db.models.deletion.CASCADE, to='athena_app_cmdb.assettype'),
        ),
        migrations.CreateModel(
            name='ProductEnvironment',
            fields=[
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('refid', models.CharField(db_column='environment_id', max_length=50)),
                ('prefix', models.CharField(blank=True, db_column='prefix', max_length=50, null=True)),
                ('deleted', models.BooleanField(db_column='deleted', default='f')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', null=True)),
                ('created_by', models.CharField(blank=True, db_column='created_by', max_length=100, null=True)),
                ('updated_by', models.CharField(blank=True, db_column='updated_by', max_length=100, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='athena_app_cmdb.location')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='environments', to='athena_app_cmdb.product')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='athena_app_cmdb.envtype')),
            ],
            options={
                'verbose_name': 'Environment',
                'db_table': 'product_environment',
                'ordering': ['product', 'type'],
                'managed': True,
                'unique_together': {('refid', 'product')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='asset',
            unique_together={('id', 'name')},
        ),
    ]
