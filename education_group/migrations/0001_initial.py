# Generated by Django 2.2.5 on 2019-12-23 14:52

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0489_auto_20191217_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('end_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='group_end_years', to='base.AcademicYear', verbose_name='End academic year')),
                ('start_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='group_start_years', to='base.AcademicYear', verbose_name='Start academic year')),
            ],
        ),
        migrations.CreateModel(
            name='GroupYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('partial_acronym', models.CharField(db_index=True, max_length=15, null=True, verbose_name='code')),
                ('acronym', models.CharField(db_index=True, max_length=40, verbose_name='code')),
                ('credits', models.PositiveIntegerField(blank=True, null=True, verbose_name='credits')),
                ('constraint_type', models.CharField(blank=True, choices=[('CREDITS', 'credits'), ('NUMBER_OF_ELEMENTS', 'Number of elements')], default=None, max_length=20, null=True, verbose_name='type of constraint')),
                ('min_constraint', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='minimum constraint')),
                ('max_constraint', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='maximum constraint')),
                ('title_fr', models.CharField(max_length=255, verbose_name='Title in French')),
                ('title_en', models.CharField(blank=True, default='', max_length=240, verbose_name='Title in English')),
                ('remark_fr', models.TextField(blank=True, default='', verbose_name='remark')),
                ('remark_en', models.TextField(blank=True, default='', verbose_name='remark in english')),
                ('education_group_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupType', verbose_name='Type of training')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='education_group.Group')),
            ],
        ),
    ]
