# Generated by Django 3.2.3 on 2021-08-20 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_auto_20210814_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.CharField(default='name', max_length=250),
            preserve_default=False,
        ),
    ]
