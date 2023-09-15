from django.db import models

# Main Order Model
class Order(models.Model):
    order_id = models.IntegerField(unique=True) 
    created_via = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    currency = models.CharField(max_length=10)
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField()
    discount_total = models.DecimalField(max_digits=10, decimal_places=2)
    discount_tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_tax = models.DecimalField(max_digits=10, decimal_places=2)
    cart_tax = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2)
    # Other fields can be added as necessary

    # Relations
    billing = models.OneToOneField('BillingProperties', on_delete=models.CASCADE, null=True, blank=True)
    shipping = models.OneToOneField('ShippingProperties', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.order_key

# Billing properties
class BillingProperties(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

# Shipping properties
class ShippingProperties(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50)

# Meta data properties
class OrderMetaData(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='meta_data')
    key = models.CharField(max_length=255)
    value = models.TextField()

# Coupon lines properties
class CouponLines(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='coupon_lines')
    code = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_tax = models.DecimalField(max_digits=10, decimal_places=2)

# Refunds properties
class Refunds(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    refund_id = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

# Taxes properties
class Taxes(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='taxes')
    rate_code = models.CharField(max_length=255)
    rate_id = models.PositiveIntegerField()
    label = models.CharField(max_length=255)
    compound = models.BooleanField()
    tax_total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_tax_total = models.DecimalField(max_digits=10, decimal_places=2)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
