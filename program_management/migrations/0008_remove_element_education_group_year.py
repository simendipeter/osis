# Generated by Django 2.2.13 on 2020-08-03 13:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('program_management', '0007_auto_20200424_1513'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='element',
            name='education_group_year',
        ),
    ]
