# Generated by Django 3.2.3 on 2021-11-13 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_alter_orderstatus_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderstatus',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_status', to='orders.order'),
        ),
    ]
