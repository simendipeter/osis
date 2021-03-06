# Generated by Django 2.2.10 on 2020-05-13 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0513_auto_20200424_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationgroupyear',
            name='isced_domain',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_ares': True}, null=True, on_delete=django.db.models.deletion.PROTECT, to='reference.DomainIsced', verbose_name='ISCED domain'),
        ),
        migrations.AlterField(
            model_name='groupelementyear',
            name='block',
            field=models.IntegerField(blank=True, null=True, verbose_name='Block'),
        ),
        migrations.AddConstraint(
            model_name='groupelementyear',
            constraint=models.CheckConstraint(check=models.Q(('child_branch__isnull', False), ('child_leaf__isnull', False), _negated=True), name='child_branch_xor_child_leaf'),
        ),
    ]
