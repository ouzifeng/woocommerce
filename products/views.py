from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductMetaData
import requests, json, ast
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from decimal import Decimal
from django.db.utils import IntegrityError
from django.db import transaction
from .sync import build_product_data, import_new_products, resync_existing_products, get_live_data




def display_products(request):
    all_products = Product.objects.all().order_by('name', 'product_id')
    paginator = Paginator(all_products, 10)  # Show 10 products per page

    page_number = request.GET.get('page')
    paginated_products = paginator.get_page(page_number)

    return render(request, 'products_table.html', {'products': paginated_products})


def fetch_live_product_data(request):
    product_ids = request.GET.get('product_ids').split(',')
    live_data = get_live_data(product_ids)
    return JsonResponse(live_data)


def import_products_view(request):
    import_new_products(request)  # Pass the request object here
    print("Products imported successfully!")
    return redirect('display_products')

def resync_products_view(request):
    resync_existing_products(request)
    print(request, "Products resynced successfully!")
    return redirect('display_products')

def get_progress(request):
    progress = request.session.get('progress', "Starting import...")
    return JsonResponse({'progress': progress})


def product_page(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    metadata = product.meta_data.all()

    raw_attributes = product.attributes or '[]'
    
    # First, try to parse it as JSON
    try:
        attributes = json.loads(raw_attributes)
    except json.JSONDecodeError:
        # If that fails, try to evaluate it as a Python expression
        try:
            attributes = ast.literal_eval(raw_attributes)
        except (SyntaxError, ValueError):
            attributes = []
            print(f"Failed to parse attributes for product {product_slug}: {raw_attributes}")

    context = {
        'product': product,
        'metadata': metadata,
        'attributes': attributes,
    }

    return render(request, 'products.html', context)


def update_products(request):
    """Update product values in the database based on discrepancies with live data."""
    product_ids = request.POST.get('product_ids').split(',')
    live_data = get_live_data(product_ids)
    print(f"Product IDs received: {product_ids}")
    
    for product_id_str in live_data:
        product_id = int(product_id_str)
        print(f"Processing product_id: {product_id}")

        product_query = Product.objects.filter(pk=product_id)
        if not product_query.exists():
            print(f"Product with ID {product_id} not found in the database!")
            continue
        
        product = product_query.first()
        data = live_data[product_id_str]

        # Initialize flags for changes
        regular_price_changed = False
        sale_price_changed = False
        stock_quantity_changed = False

        # Handle regular_price
        if data['regular_price'] not in [None, ''] and product.regular_price != Decimal(data['regular_price']):
            product.regular_price = Decimal(data['regular_price'])
            regular_price_changed = True

        # Handle sale_price
        if data['sale_price'] in [None, '']:
            if product.sale_price not in [None, '']:
                product.sale_price = None
                sale_price_changed = True
        elif product.sale_price != Decimal(data['sale_price']):
            product.sale_price = Decimal(data['sale_price'])
            sale_price_changed = True

        # Handle stock_quantity
        if data['stock_quantity'] is not None and product.stock_quantity != int(data['stock_quantity']):
            product.stock_quantity = int(data['stock_quantity'])
            stock_quantity_changed = True

        # If any field was updated, save the product
        if regular_price_changed or sale_price_changed or stock_quantity_changed:
            try:
                product.save()
                print(f"Updated product {product_id}:")
                if regular_price_changed:
                    print(f"    Regular Price updated to {product.regular_price}")
                if sale_price_changed:
                    print(f"    Sale Price updated to {product.sale_price}")
                if stock_quantity_changed:
                    print(f"    Stock Quantity updated to {product.stock_quantity}")
            except Exception as e:
                print(f"Error updating product {product_id}: {e}")

    return JsonResponse({'status': 'success'})

def landing_page(request):
    return render(request, 'index.html')