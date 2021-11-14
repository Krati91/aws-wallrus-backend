from django.contrib import admin

from .models import DesignTag, Design, Colorway
# Register your models here.


class DesignTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'label']
    search_fields = ['name', 'label']


admin.site.register(DesignTag, DesignTagAdmin)


class Colorway(admin.TabularInline):
    model = Colorway


class DesignAdmin(admin.ModelAdmin):
    inlines = [Colorway]

    class Meta:
        model = Design


admin.site.register(Design, DesignAdmin)
