# Generated by Django 3.2.3 on 2021-06-30 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_auto_20210629_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]