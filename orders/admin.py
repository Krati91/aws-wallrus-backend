from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

# Register your models here.
from .models import *

admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(MeasurementRequest)

class OrderStatus(admin.StackedInline):
    model = OrderStatus


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    inlines = [OrderStatus]
