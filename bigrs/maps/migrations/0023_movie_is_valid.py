# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-24 13:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0022_auto_20170621_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='is_valid',
            field=models.BooleanField(default=True),
        ),
    ]