# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-08-24 14:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldreference',
            name='context',
            field=models.CharField(blank=True, choices=[('TRAINING_DAILY_MANAGEMENT', 'Training management day-to-day'), ('TRAINING_PROPOSAL_MANAGEMENT', 'Training management during proposal stage'), ('TRAINING_PGRM_ENCODING_PERIOD', 'Training management during program type encoding period'), ('MINI_TRAINING_DAILY_MANAGEMENT', 'Mini-training management day-to-day'), ('MINI_TRAINING_PROPOSAL_MANAGEMENT', 'Mini-training management during proposal stage'), ('MINI_TRAINING_PGRM_ENCODING_PERIOD', 'Mini-training management during program type encoding period'), ('GROUP_DAILY_MANAGEMENT', 'Group management day-to-day'), ('GROUP_PROPOSAL_MANAGEMENT', 'Group management during proposal stage'), ('GROUP_PGRM_ENCODING_PERIOD', 'Group management during program type encoding period')], max_length=50),
        ),
    ]
