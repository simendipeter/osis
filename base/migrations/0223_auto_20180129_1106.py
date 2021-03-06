# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-29 10:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0222_auto_20180125_0923'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='learningunit',
            options={'permissions': (('can_access_learningunit', 'Can access learning unit'), ('can_edit_learningunit_date', 'Can edit learning unit date'), ('can_edit_learningunit_pedagogy', 'Can edit learning unit pedagogy'), ('can_edit_learningunit_specification', 'Can edit learning unit specification'), ('can_delete_learningunit', 'Can delete learning unit'), ('can_propose_learningunit', 'Can propose learning unit '), ('can_create_learningunit', 'Can create learning unit'))},
        ),
        migrations.AlterUniqueTogether(
            name='learningunityear',
            unique_together=set([('learning_unit', 'academic_year', 'deleted')]),
        ),
    ]
