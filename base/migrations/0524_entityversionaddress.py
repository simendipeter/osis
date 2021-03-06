# Generated by Django 2.2.13 on 2020-07-17 16:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0523_merge_20200703_1533'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entityversionaddress',
            old_name='entity_version_id',
            new_name='entity_version',
        ),
        migrations.AddConstraint(
            model_name='entityversionaddress',
            constraint=models.UniqueConstraint(
                condition=models.Q(is_main=True),
                fields=('entity_version',),
                name='unique_main_address')
            ,
        ),
    ]
