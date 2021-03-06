# Generated by Django 3.2.3 on 2021-06-15 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('designs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='design',
            name='materials',
            field=models.ManyToManyField(to='product.Material'),
        ),
        migrations.AddField(
            model_name='design',
            name='products',
            field=models.ManyToManyField(to='product.Product'),
        ),
    ]
