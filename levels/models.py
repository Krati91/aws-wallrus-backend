from django.db import models

# Create your models here.

NAME_CHOICES = [
    (1, 'Entry Level'),
    (2, 'Silver'),
    (3, 'Gold'),
    (4, 'Platinum')
]


class Group(models.Model):
    name = models.IntegerField(choices=NAME_CHOICES)
    start_point = models.IntegerField()
    end_point = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.get_name_display()


class RoyaltyGroup(Group):
    royalty_percent = models.DecimalField(max_digits=5, decimal_places=2)


class CommissionGroup(Group):
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2)
