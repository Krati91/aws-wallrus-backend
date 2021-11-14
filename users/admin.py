from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import *
# Register your models here.
from user_details.admin import BankDetail, BusinessDetail
from notifications.admin import ArtistNotificationSettings


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Information'), {
            'fields': ('profile_picture', 'first_name', 'last_name', 'phone', 'username', 'type', 'bio', 'Unique_id')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
                                       'is_superuser', 'groups', 'user_permissions')}),
        (_('Login Details'), {'fields': ('date_joined', 'last_login')})
    )
    inlines = [BusinessDetail, BankDetail]
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('email', 'password1', 'password2', 'type')
        }),
    )

    list_display = ('id', 'email', 'phone', 'first_name', 'last_name', 'type')
    search_fields = ('email', 'phone')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RandomPassword)
admin.site.register(Code)
admin.site.register(Firm)
admin.site.register(Interior_Decorator)


@admin.register(Artist)
class ArtistAdmin(ModelAdmin):
    inlines = [ArtistNotificationSettings]
