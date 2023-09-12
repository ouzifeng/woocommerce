from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Product(models.Model):
    product_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    permalink = models.URLField()
    type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    description = models.TextField()
    short_description = models.TextField()
    sku = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_sales = models.IntegerField()
    stock_quantity = models.IntegerField(null=True, blank=True)
    stock_status = models.CharField(max_length=50)
    weight = models.CharField(max_length=50, null=True, blank=True)
    shipping_class = models.CharField(max_length=100, null=True, blank=True)
    parent_id = models.IntegerField(null=True, blank=True)
    categories = models.TextField()  # Can be improved with a ForeignKey for actual categories
    images = models.URLField()  # The source URL of the main image
    attributes = models.TextField()  # JSON-like text field or can be improved with a ForeignKey or ManyToMany relationship
    default_attributes = models.TextField()
    variations = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.name)
            self.slug = original_slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super(Product, self).save(*args, **kwargs)


    def __str__(self):
        return self.name

class UserColumnPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    column_name = models.CharField(max_length=255)
    is_visible = models.BooleanField(default=True)
    
    