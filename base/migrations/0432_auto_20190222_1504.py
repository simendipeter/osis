# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-02-27 09:32
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0431_auto_20190220_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationrule',
            name='help_text_en',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='english help text'),
        ),
        migrations.AddField(
            model_name='validationrule',
            name='help_text_fr',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='french help text'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='decree_category',
            field=models.CharField(blank=True, choices=[('FCONT', 'FCONT - Formation continue (non académique)'), ('BAS1', 'BAS1 - Etudes de base de premier cycle'), ('BAS2', 'BAS2 - Etudes de base de deuxième cycle'), ('AESS', 'AESS - A.E.S.S.'), ('DEC1', 'DEC1 - Etudes complémentaires de premier cycle'), ('DEC2', 'DEC2 - Etudes complémentaires de deuxième cycle'), ('DES', 'DES - Etudes spécialisées de troisième cycle'), ('DEA', 'DEA - Etudes approfondies de troisième cycle'), ('DOC', 'DOC - Docteur'), ('AES', 'AES - A.E.S.'), ('AUTRE', 'AUTRE - Autre (non académique)'), ('BAC', 'BAC - Bachelier'), ('AP2C', 'AP2C - Année préparatoire à un 2ème cycle'), ('MA1', 'MA1 - Master en 60 crédits'), ('MA2X', 'MA2X - Master en 120 crédits'), ('MA2D', 'MA2D - Master en 120 crédits à finalité didactique'), ('MA2S', 'MA2S - Master en 120 crédits à finalité spécialisée'), ('MA2A', 'MA2A - Master en 120 crédits à finalité approfondie'), ('MA2M', 'MA2M - Master en 180 ou 240 crédits'), ('AS2C', 'AS2C - Année supplémentaire à un 2ème cycle'), ('MACO', 'MACO - Master complémentaire'), ('AESSB', "AESSB - Agrégation de l'enseignement secondaire supérieur (AESS)"), ('CAPS', "CAPS - Certificat d'aptitude pédagogique approprié à l'enseignement supérieur (CAPAES)"), ('AS3C', 'AS3C - Année supplémentaire à un 3ème cycle'), ('FODO', 'FODO - Formations doctorales (Certificat de formation à la recherche)'), ('CEMC', 'CEMC - Certificats de médecine clinique / Certificats interuniversitaires de formation médicale spécialisée'), ('MED', 'MED - Médecin'), ('VETE', 'VETE - Médecin vétérinaire')], max_length=40, null=True, verbose_name='Decree category'),
        ),
    ]
