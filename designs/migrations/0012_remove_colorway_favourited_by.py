# Generated by Django 3.2.3 on 2021-11-20 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('designs', '0011_design_designs_des_slug_74d3bd_idx'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='colorway',
            name='favourited_by',
        ),
    ]
