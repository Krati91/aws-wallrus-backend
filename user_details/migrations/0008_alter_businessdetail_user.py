# Generated by Django 3.2.3 on 2021-11-13 08:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_details', '0007_alter_businessdetail_gst_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessdetail',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='business_details', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
