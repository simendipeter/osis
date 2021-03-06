# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-16 10:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0390_auto_20181116_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='authorizedrelationship',
            name='max_count_authorized',
            field=models.CharField(choices=[('1', 'One'), ('MANY', 'Many')], default='MANY', max_length=5),
        ),
        migrations.AddField(
            model_name='authorizedrelationship',
            name='min_count_authorized',
            field=models.CharField(choices=[('0', 'Zero'), ('1', 'One')], default='0', max_length=5),
        ),
    ]