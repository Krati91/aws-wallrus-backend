# Generated by Django 3.2.3 on 2021-08-20 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('designs', '0009_designtag_designs_des_name_fa1665_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='design',
            name='slug',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
