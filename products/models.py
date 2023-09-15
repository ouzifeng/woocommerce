from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Product(models.Model):
    product_id = models.IntegerField(unique=True, primary_key=True)
    name = models.TextField()
    permalink = models.URLField(max_length=1000)
    type = models.TextField()
    status = models.TextField()
    description = models.TextField()
    short_description = models.TextField()
    sku = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_sales = models.IntegerField()
    stock_quantity = models.IntegerField(null=True, blank=True)
    stock_status = models.TextField()
    weight = models.TextField(null=True, blank=True)
    shipping_class = models.TextField(null=True, blank=True)
    parent_id = models.IntegerField(null=True, blank=True)
    categories = models.TextField()  # Can be improved with a ForeignKey for actual categories
    images = models.URLField(max_length=5000)
    attributes = models.TextField()  # JSON-like text field or can be improved with a ForeignKey or ManyToMany relationship
    variations = models.TextField()
    slug = models.SlugField(unique=True, blank=True, max_length=500)

    
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
    
class ProductMetaData(models.Model):
    key = models.TextField()
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    
    product = models.ForeignKey(Product, related_name='meta_data', on_delete=models.CASCADE)    

class UserColumnPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    column_name = models.CharField(max_length=1000)
    is_visible = models.BooleanField(default=True)
    
    