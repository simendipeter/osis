# Generated by Django 2.2.5 on 2020-01-06 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0489_auto_20191217_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningunit',
            name='existing_proposal_in_epc',
        ),
    ]
