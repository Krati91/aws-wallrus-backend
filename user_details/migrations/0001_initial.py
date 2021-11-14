# Generated by Django 3.2.3 on 2021-07-09 15:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0015_remove_customuser_personal_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessDetail',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='users.customuser')),
                ('pan_card_number', models.CharField(max_length=150, unique=True)),
                ('brand_name', models.CharField(max_length=150)),
                ('gst_number', models.CharField(max_length=150)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
            ],
        ),
        migrations.CreateModel(
            name='BankDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('branch', models.CharField(max_length=255)),
                ('ifsc_code', models.CharField(default='BKID', max_length=255)),
                ('swift_code', models.CharField(max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, 'Personal Address'), (2, 'Business Address'), (3, 'Shipping Address'), (4, 'Billing Address')], default=1)),
                ('line1', models.TextField()),
                ('line2', models.TextField()),
                ('city', models.CharField(max_length=150)),
                ('state', models.CharField(max_length=150)),
                ('pincode', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]