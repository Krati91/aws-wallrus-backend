from django.db import models

from user_details.models import Address
from product.models import Product
from users.models import CustomUser
# Create your models here.


class Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    width = models.CharField(max_length=5)
    height = models.CharField(max_length=5)


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered')
]


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)
    billing_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, limit_choices_to={'type': 4}, related_name='billing_address')
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, limit_choices_to={'type': 3}, related_name='shipping_address')
    created_at = models.DateField(auto_now_add=True)


class OrderStatus(models.Model):
    order = models.ForeignKey(
        Order, related_name='order_status', on_delete=models.CASCADE)
    name = models.CharField(max_length=10, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Order Status'
