# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-02 12:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0055_message_history_modifications'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='academiccalendar',
            options={'permissions': (('can_access_academic_calendar', 'Can access academic calendar'),)},
        ),
        migrations.AlterModelOptions(
            name='academicyear',
            options={'permissions': (('can_access_academicyear', 'Can access academic year'),)},
        ),
        migrations.AlterModelOptions(
            name='learningunit',
            options={'permissions': (('can_access_learningunit', 'Can access learning unit'),)},
        ),
        migrations.AlterModelOptions(
            name='offer',
            options={'permissions': (('can_access_offer', 'Can access offer'), ('can_access_catalog', 'Can access catalog'), )},
        ),
        migrations.AlterModelOptions(
            name='offerenrollment',
            options={'permissions': (('can_access_student_path', 'Can access student path'), ('can_access_evaluation', 'Can access evaluation'))},
        ),
        migrations.AlterModelOptions(
            name='organization',
            options={'permissions': (('can_access_organization', 'Can access organization'),)},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'permissions': (('is_administrator', 'Is administrator'),)},
        ),
        migrations.AlterModelOptions(
            name='scoresencoding',
            options={'managed': False, 'permissions': (('can_access_scoreencoding', 'Can access scoreencoding'),)},
        ),
        migrations.AlterModelOptions(
            name='structure',
            options={'permissions': (('can_access_structure', 'Can access structure'),)},
        ),
    ]
