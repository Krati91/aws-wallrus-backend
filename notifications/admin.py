from django.contrib import admin

# Register your models here.
from .models import ArtistNotificationSettings


class ArtistNotificationSettings(admin.StackedInline):
    model = ArtistNotificationSettings
