# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-04-04 09:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0441_auto_20190325_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='programmanager',
            name='is_main',
            field=models.BooleanField(default=False, verbose_name='Main'),
        ),
    ]
