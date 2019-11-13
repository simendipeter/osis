# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-28 13:42
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0195_auto_20171124_1018'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalFolder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('folder_id', models.IntegerField()),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Entity')),
            ],
        ),
        migrations.CreateModel(
            name='ProposalLearningUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('CREATION', 'CREATION'), ('MODIFICATION', 'MODIFICATION'), ('TRANSFORMATION', 'TRANSFORMATION'), ('TRANSFORMATION_AND_MODIFICATION', 'TRANSFORMATION_AND_MODIFICATION'), ('SUPPRESSION', 'SUPPRESSION')], max_length=50)),
                ('state', models.CharField(choices=[('FACULTY', 'FACULTY'), ('CENTRAL', 'CENTRAL'), ('SUSPENDED', 'SUSPENDED'), ('ACCEPTED', 'ACCEPTED'), ('REFUSED', 'REFUSED')], max_length=50)),
                ('initial_data', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Person')),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.ProposalFolder')),
                ('learning_unit_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitYear')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='proposalfolder',
            unique_together=set([('entity', 'folder_id')]),
        ),
    ]
