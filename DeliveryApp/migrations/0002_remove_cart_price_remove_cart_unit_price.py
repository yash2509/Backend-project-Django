# Generated by Django 4.2.10 on 2024-02-22 11:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DeliveryApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='price',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='unit_price',
        ),
    ]
