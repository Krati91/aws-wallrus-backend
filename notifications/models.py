from django.db import models

from users.models import Artist
# Create your models here.

frequency_status = [
    (1, 'Immediately'),
    (2, 'Daily'),
    (3, 'Weekly'),
    (4, 'Monthly')
]


class ArtistNotificationSettings(models.Model):
    user = models.OneToOneField(Artist, on_delete=models.CASCADE)
    follower_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    payment_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    design_view_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    design_favorite_frequency = models.IntegerField(
        choices=frequency_status, default=1)
    design_purchase_frequency = models.IntegerField(
        choices=frequency_status, default=1)

    class Meta:
        verbose_name_plural = 'Artist notification settings'

    def __str__(self):
        return self.user.user.email
