# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-15 15:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0002_auto_20160215_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singleproduct',
            name='sale_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
