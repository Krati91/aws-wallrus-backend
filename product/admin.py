from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Application)


class ProductImageAdmin(admin.StackedInline):
    model = ProductImages


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]


admin.site.register(Tag)

admin.site.register(Reviews)
