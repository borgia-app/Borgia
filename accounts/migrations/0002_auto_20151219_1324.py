# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-19 12:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='campus',
            field=models.CharField(blank=True, max_length=4),
        ),
        migrations.AlterField(
            model_name='user',
            name='family',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='surname',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]