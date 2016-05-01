# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-01 17:26
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0037_auto_20160427_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetemplate',
            name='template',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='student',
            name='registration_id',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
