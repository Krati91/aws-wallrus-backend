# Generated by Django 3.2.3 on 2021-11-08 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_alter_interior_decorator_firm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interior_decorator',
            name='firm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.firm'),
        ),
    ]
