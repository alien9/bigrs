# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-10 22:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0018_spot_bi'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='is_contado',
            field=models.BooleanField(default=False),
        ),
    ]