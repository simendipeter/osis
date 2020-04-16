# Generated by Django 2.2.10 on 2020-03-30 13:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program_management', '0004_auto_20200323_1055'),
        ('base', '0509_postgis_extension'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupelementyear',
            name='child_element',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children_elements', to='program_management.Element'),
        ),
        migrations.AddField(
            model_name='groupelementyear',
            name='parent_element',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parent_elements', to='program_management.Element'),
        ),
    ]