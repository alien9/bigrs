# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-26 05:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0013_auto_20170426_0440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spot',
            name='keys',
            field=models.ManyToManyField(blank=True, to='maps.Key'),
        ),
    ]
