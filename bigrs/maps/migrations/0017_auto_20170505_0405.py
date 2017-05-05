# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-05 04:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0016_auto_20170503_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='contado',
            name='movie',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='maps.Movie'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contado',
            name='timestamp',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
