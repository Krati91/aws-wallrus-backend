from django.db import models
from django.utils.text import slugify

from users.models import CustomUser
from product.models import Application


class DesignTag(models.Model):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=['name'])]


class Design(models.Model):
    artist = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    applications = models.ManyToManyField(Application)
    tags = models.ManyToManyField(DesignTag)
    is_customizable = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f'{self.name} uploaded by {self.artist.email}'

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.artist.type == 2:
                self.is_public = False

        if not self.slug:
            self.slug = slugify(self.name + ' by ' + self.get_artist_name())
        super().save(*args, **kwargs)
        super().save(*args, **kwargs)

    def get_artist_name(self):
        return self.artist.first_name + ' ' + self.artist.last_name

    class Meta:
        indexes = [models.Index(fields=['slug'])]


def image_upload_to(instance, filename):
    return f'designs/{instance.collection.artist.id}/{instance.collection.id}/{filename}'


class Colorway(models.Model):
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    image_url = models.URLField()
    color_tags = models.ManyToManyField(
        DesignTag, limit_choices_to={'label': 'Color'})
    favourited_by = models.ManyToManyField(CustomUser, limit_choices_to={
        'type': 2}, blank=True)

    def __str__(self):
        return f'{self.name}'
