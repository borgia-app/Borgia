# Generated by Django 2.1.10 on 2019-11-20 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0002_categoryproduct_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categoryproduct',
            name='order',
        ),
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]