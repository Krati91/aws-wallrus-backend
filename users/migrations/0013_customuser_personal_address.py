# Generated by Django 3.2.3 on 2021-07-04 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_remove_artist_firm'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='personal_address',
            field=models.CharField(default='dsds', max_length=256),
        ),
    ]
