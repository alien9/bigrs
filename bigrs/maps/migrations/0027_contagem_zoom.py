# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-09 13:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0026_remove_spot_geom'),
    ]

    operations = [
        migrations.AddField(
            model_name='contagem',
            name='zoom',
            field=models.IntegerField(default=18),
        ),
    ]
