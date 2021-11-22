from django.db import models
from django.utils.text import slugify

from users.models import CustomUser
# Create your models here.


class Application(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        indexes = [models.Index(fields=['slug'])]


class Tag(models.Model):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=['name'])]


class Product(models.Model):
    sku = models.BigAutoField(primary_key=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    design = models.ForeignKey("designs.Design", on_delete=models.CASCADE)
    colorway = models.ForeignKey("designs.Colorway", on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    material = models.CharField(max_length=255)
    cost = models.IntegerField()
    views = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    slug = models.CharField(max_length=250, null=True, blank=True)
    slug_tag = models.CharField(max_length=250, null=True, blank=True)
    favourited_by = models.ManyToManyField(CustomUser, limit_choices_to={
        'type': 2}, blank=True)

    def __str__(self):
        return f'{self.design.name}.{self.colorway.name}.{self.application}'

    def get_slug(self):
        slug = ''
        try:
            for items in self.tags.all():
                slug += items.name+' '
        except:
            pass

        return slugify(slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f'{self.design.name} {self.colorway.name} {self.application}')
        elif not self.slug_tag:
            self.slug_tag = self.get_slug()
        super().save(*args, **kwargs)

    def get_artist_name(self):
        return self.design.artist.first_name + ' ' + self.design.artist.last_name

    def get_display_image(self):
        return self.productimages_set.values_list('image', flat=True).first()

    def get_number_of_ratings(self):
        total = 0
        for review in self.reviews_set.all():
            total += review.rating
        return total

    def get_average_rating(self):
        total = 0
        for review in self.reviews_set.all():
            total += review.rating
        return "{:.1f}".format(total / self.reviews_set.count()) if self.reviews_set.count() else 0

    def get_base_cost(self):
        artist_royalty_percent = self.design.artist.artist.get_royalty_percent()
        base_cost = self.cost - (artist_royalty_percent * self.cost / 100)
        return int(base_cost)

    class Meta:
        indexes = [models.Index(fields=['slug'])]


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    class Meta:
        verbose_name_plural = 'Product Images'


class Reviews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    review = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.reviewer.first_name} {self.reviewer.last_name} for {self.product.design.name}.{self.product.colorway.name}.{self.product.application}'

    def get_reviewer_name(self):
        return f'{self.reviewer.first_name} {self.reviewer.last_name}'

    def get_reviewer_picture(self):
        return f'{self.reviewer.profile_picture}'

    class Meta:
        verbose_name_plural = 'Reviews'


class Collection(models.Model):
    user = models.ForeignKey(CustomUser, limit_choices_to={
                             'type': 2}, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    products = models.ManyToManyField(Product)
