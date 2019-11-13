# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-08-22 09:51
from __future__ import unicode_literals

from django.db import migrations


def convert_none_to_empty(apps, schema_editor):
    EducationGroupYear = apps.get_model("base", "EducationGroupYear")
    db_alias = schema_editor.connection.alias

    EducationGroupYear.objects.using(db_alias).filter(diploma_printing_title=None).update(diploma_printing_title="")
    EducationGroupYear.objects.using(db_alias).filter(funding_direction=None).update(funding_direction="")
    EducationGroupYear.objects.using(db_alias).filter(funding_direction_cud=None).update(funding_direction_cud="")
    EducationGroupYear.objects.using(db_alias).filter(inter_organization_information=None).update(inter_organization_information="")
    EducationGroupYear.objects.using(db_alias).filter(keywords=None).update(keywords="")
    EducationGroupYear.objects.using(db_alias).filter(professional_title=None).update(professional_title="")
    EducationGroupYear.objects.using(db_alias).filter(remark=None).update(remark="")
    EducationGroupYear.objects.using(db_alias).filter(remark_english=None).update(remark_english="")
    EducationGroupYear.objects.using(db_alias).filter(title_english=None).update(title_english="")


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0334_auto_20180821_0935'),
    ]

    operations = [
        migrations.RunPython(convert_none_to_empty),
    ]
