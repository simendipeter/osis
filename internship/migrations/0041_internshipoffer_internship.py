# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-05 07:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0040_auto_20170405_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='internshipoffer',
            name='internship',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='internship.Internship'),
        ),
    ]
