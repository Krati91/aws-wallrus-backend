# Generated by Django 3.2.3 on 2021-11-13 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_orderstatus_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_cost',
        ),
    ]
