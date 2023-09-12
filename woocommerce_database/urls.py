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
from django.urls import path
from products import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('products/', views.display_products, name='display_products'),
    path('import_products/', views.import_products_view, name='import_products'),
    path('resync_products/', views.resync_products_view, name='resync_products'),
    path('get-progress/', views.get_progress, name='get_progress'),
    path('product-page/<str:product_name>/', views.product_page, name='product_page'),
]
