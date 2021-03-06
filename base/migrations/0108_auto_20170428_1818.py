# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-28 16:18
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0107_learningunit_learning_container'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntityManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
            ],
            options={
                'permissions': (('is_entity_manager', 'Is entity manager '),),
            },
        ),
        migrations.AddField(
            model_name='person',
            name='employee',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='entitymanager',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Person'),
        ),
        migrations.AddField(
            model_name='entitymanager',
            name='structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Structure'),
        ),
    ]
