# Generated by Django 3.2.9 on 2022-01-05 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('athena_app_cmdb', '0009_alter_onboardingrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onboardingrequest',
            name='datetime_approved',
            field=models.DateTimeField(blank=True, db_column='datetime_approved', null=True),
        ),
        migrations.AlterField(
            model_name='onboardingrequest',
            name='datetime_completed',
            field=models.DateTimeField(blank=True, db_column='datetime_completed', null=True),
        ),
        migrations.AlterField(
            model_name='onboardingrequest',
            name='datetime_rejected',
            field=models.DateTimeField(blank=True, db_column='datetime_rejected', null=True),
        ),
    ]
