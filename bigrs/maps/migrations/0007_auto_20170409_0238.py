# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-09 02:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0006_spot'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spot',
            name='location',
        ),
        migrations.AddField(
            model_name='spot',
            name='x',
            field=models.DecimalField(decimal_places=10, default=867, max_digits=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='spot',
            name='y',
            field=models.DecimalField(decimal_places=10, default=876, max_digits=30),
            preserve_default=False,
        ),
    ]
