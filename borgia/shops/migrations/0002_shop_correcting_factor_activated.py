# Generated by Django 2.1.10 on 2022-03-31 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='correcting_factor_activated',
            field=models.BooleanField(default=True, verbose_name='Activation du facteur de correction'),
        ),
    ]