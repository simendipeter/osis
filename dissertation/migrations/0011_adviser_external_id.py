# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-23 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0010_auto_20160816_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='adviser',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
