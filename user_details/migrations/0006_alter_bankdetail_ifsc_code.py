# Generated by Django 3.2.3 on 2021-07-09 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_details', '0005_bankdetail_ifsc_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankdetail',
            name='ifsc_code',
            field=models.CharField(max_length=255),
        ),
    ]
