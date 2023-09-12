from django.contrib import admin, messages
from .models import Product
from .views import fetch_products_from_woocommerce

def import_products(modeladmin, request, queryset):
    # Notify start of import
    modeladmin.message_user(request, "Products import initiated.")
    
    # Call the function to fetch products
    fetch_products_from_woocommerce()
    
    # Notify end of import
    modeladmin.message_user(request, "Products import completed.")

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'type', 'sku', 'price']
    actions = [import_products]

admin.site.register(Product, ProductAdmin)
