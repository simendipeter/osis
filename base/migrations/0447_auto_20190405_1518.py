# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-04-05 15:18
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0446_populate_learning_unit_year'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningunitcomponent',
            name='learning_component_year',
        ),
        migrations.RemoveField(
            model_name='learningunitcomponent',
            name='learning_unit_year',
        ),
        migrations.RemoveField(
            model_name='learningunitcomponentclass',
            name='learning_class_year',
        ),
        migrations.RemoveField(
            model_name='learningunitcomponentclass',
            name='learning_unit_component',
        ),
        migrations.RemoveField(
            model_name='learningunityear',
            name='learning_component_years',
        ),
        migrations.AlterField(
            model_name='learningcomponentyear',
            name='learning_container_year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.LearningContainerYear'),
        ),
        migrations.AlterField(
            model_name='programmanager',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Person', verbose_name='person'),
        ),
        migrations.DeleteModel(
            name='LearningUnitComponent',
        ),
        migrations.DeleteModel(
            name='LearningUnitComponentClass',
        ),
    ]
