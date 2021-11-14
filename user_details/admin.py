from django.contrib import admin

from .models import Address, BusinessDetail, BankDetail
# Register your models here.

admin.site.register(Address)


class BusinessDetail(admin.StackedInline):
    model = BusinessDetail


class BankDetail(admin.StackedInline):
    model = BankDetail
