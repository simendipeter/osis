# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-01-28 16:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0004_auto_20180807_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoresheetaddress',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='scoresheetaddress',
            name='fax',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Fax'),
        ),
        migrations.AlterField(
            model_name='scoresheetaddress',
            name='phone',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Phone'),
        ),
    ]