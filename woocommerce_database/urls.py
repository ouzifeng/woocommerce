"""
URL configuration for woocommerce_database project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from products import views as product_views
from orders import views as order_views



urlpatterns = [
    path("admin/", admin.site.urls),
    path('products/', product_views.display_products, name='display_products'),
    path('import_products/', product_views.import_products_view, name='import_products'),
    path('resync_products/', product_views.resync_products_view, name='resync_products'),
    path('get-progress/', product_views.get_progress, name='get_progress'),
    path('product-page/<slug:product_slug>/', product_views.product_page, name='product_page'),
    path('fetch-live-product-data/', product_views.fetch_live_product_data, name='fetch_live_product_data'),
    path('update-products/', product_views.update_products, name='update_products'),
    path('orders/', order_views.display_orders, name='display_orders'),
    path('import_orders/', order_views.import_orders_view, name='import_orders'),
    path('order_details/<int:order_id>/', order_views.order_details, name='order_details'),
    path('', product_views.landing_page, name='landing_page'),
]
