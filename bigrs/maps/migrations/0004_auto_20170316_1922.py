# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-16 19:22
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0003_contagem_movie'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contagem',
            options={'verbose_name_plural': 'Contagens'},
        ),
        migrations.AddField(
            model_name='contagem',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
