from django.db import models
from django.utils.translation import ugettext_lazy as _

from users.models import CustomUser, Artist, Interior_Decorator, Firm

# Create your models here.

ADDRESS_TYPE = [
    (1, 'Personal Address'),
    (2, 'Business Address'),
    (3, 'Shipping Address'),
    (4, 'Billing Address')
]


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.IntegerField(choices=ADDRESS_TYPE, default=1)
    line1 = models.TextField()
    line2 = models.TextField()
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    pincode = models.IntegerField()

    def __str__(self):
        return f'{self.user.username}({self.get_type_display()})'


class BusinessDetail(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name='business_details', on_delete=models.CASCADE, primary_key=True)
    pan_card_number = models.CharField(max_length=150, unique=True)
    brand_name = models.CharField(max_length=150)
    gst_number = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(_('email address'))

    def __str__(self):
        return f'{self.user.email}({self.brand_name})'


class BankDetail(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name='bank_details', on_delete=models.CASCADE)
    account_number = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    swift_code = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email
