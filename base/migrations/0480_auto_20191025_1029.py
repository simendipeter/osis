# Generated by Django 2.2.5 on 2019-10-25 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0479_auto_20190904_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupelementyear',
            name='is_mandatory',
            field=models.BooleanField(default=True, verbose_name='Mandatory'),
        ),
    ]