# Generated by Django 2.2.13 on 2020-07-31 10:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0528_adapt_prerequisite_for_versions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examenrollment',
            name='score_draft',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0, message='Les notes doivent être comprises entre 0 et 20'), django.core.validators.MaxValueValidator(20, message='Les notes doivent être comprises entre 0 et 20')]),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='score_final',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0, message='Les notes doivent être comprises entre 0 et 20'), django.core.validators.MaxValueValidator(20, message='Les notes doivent être comprises entre 0 et 20')]),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='score_reencoded',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0, message='Les notes doivent être comprises entre 0 et 20'), django.core.validators.MaxValueValidator(20, message='Les notes doivent être comprises entre 0 et 20')]),
        ),
    ]
