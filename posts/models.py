from django.db import models
from django.utils.text import slugify


CATEGORY_CHOICES = [
    ('blog', 'Blog'),
    ('seminar', 'Seminar'),
    ('news_letter', 'News Letter')
]


class Post(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=12)
    content = models.TextField()
    slug = models.SlugField(blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        indexes = [models.Index(fields=['slug'])]
