# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-12 12:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0061_auto_20160902_1639'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentfile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='messagehistory',
            name='person',
        ),
        migrations.DeleteModel(
            name='MessageTemplate',
        ),
        migrations.DeleteModel(
            name='DocumentFile',
        ),
        migrations.DeleteModel(
            name='MessageHistory',
        ),
    ]
