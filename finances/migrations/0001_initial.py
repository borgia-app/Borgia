# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-15 13:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('cashed', models.BooleanField(default=False)),
                ('date_cash', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cheque',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=7)),
                ('date_sign', models.DateField(default=django.utils.timezone.now)),
                ('amount', models.FloatField()),
                ('date_cash', models.DateField(blank=True, null=True)),
                ('cashed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DebitBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Lydia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_operation', models.DateField(default=django.utils.timezone.now)),
                ('time_operation', models.TimeField(default=django.utils.timezone.now)),
                ('amount', models.FloatField()),
                ('cashed', models.BooleanField(default=False)),
                ('date_cash', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('done', models.BooleanField(default=False)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finances.Payment')),
            ],
        ),
    ]
