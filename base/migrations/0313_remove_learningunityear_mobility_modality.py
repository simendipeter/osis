# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-07-23 11:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0312_educationgroupyear_languages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningunityear',
            name='mobility_modality',
        ),
    ]
