# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-16 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0117_auto_20170516_0919'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningcomponent',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='learningcomponentyear',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),

    ]
