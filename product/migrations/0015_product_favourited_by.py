# Generated by Django 3.2.3 on 2021-11-20 13:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0014_product_slug_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='favourited_by',
            field=models.ManyToManyField(blank=True, limit_choices_to={'type': 2}, to=settings.AUTH_USER_MODEL),
        ),
    ]