from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductMetaData
import requests
import time
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal, InvalidOperation



def build_product_data(product, product_type='product', variation=None):
    # Common fields for both product and variation
    data = {
        'product_id': product['id'],
        'name': product.get('name', ''),
        'permalink': product.get('permalink', ''),
        'type': product.get('type', ''),
        'status': product.get('status', ''),
        'description': product.get('description', ''),
        'short_description': product.get('short_description', ''),
        'sku': product.get('sku', ''),
        'price': product.get('price', '0.0') or '0.0',
        'regular_price': product.get('regular_price', '0.0') or '0.0',
        'sale_price': product.get('sale_price', '0.0') or '0.0',
        'total_sales': product.get('total_sales', 0),
        'stock_quantity': product.get('stock_quantity', 0),
        'stock_status': product.get('stock_status', ''),
        'weight': product.get('weight', ''),
        'shipping_class': product.get('shipping_class', ''),
        'parent_id': product.get('parent_id', None),
        'categories': ",".join([cat['name'] for cat in product.get('categories', [])]),
        'images': ','.join([img['src'] for img in product.get('images', [])]),
        'attributes': str(product.get('attributes', [])),
        'default_attributes': str(product.get('default_attributes', [])),
        'variations': str(product.get('variations', []))
    }

    # Extract meta data
    meta_data_list = product.get('meta_data', [])

    if product_type == 'variation' and variation:
        attributes = ", ".join([f"{attr['name']}:{attr['option']}" for attr in variation.get('attributes', [])])
        variation_name = f"{product['name']} ({attributes})" if attributes else product['name']
        data.update({
            'product_id': variation['id'],
            'name': variation_name,
            'type': 'variation',
            'status': variation.get('status', ''),
            'sku': variation.get('sku', ''),
            'price': variation.get('price', '0.0') or '0.0',
            'regular_price': variation.get('regular_price', '0.0') or '0.0',
            'sale_price': variation.get('sale_price', '0.0') or '0.0',
            'stock_quantity': variation.get('stock_quantity', 0),
            'stock_status': variation.get('stock_status', ''),
            'weight': variation.get('weight', ''),
            'shipping_class': variation.get('shipping_class', ''),
            'images': variation['image']['src'] if variation.get('image', None) else '',
            'attributes': str(variation.get('attributes', [])),
            'parent_id': product['id']
        })

        # Add variation's meta data to the list
        meta_data_list += variation.get('meta_data', [])

    return data, meta_data_list


def import_new_products(request):
    base_url = "https://www.c2kft.co.uk/wp-json/wc/v3/"
    product_url = base_url + "products"
    params = {
        "consumer_key": "ck_3f9848c65bd04057454cc23cf514d0e0abb5bf3a",
        "consumer_secret": "cs_d2eec78a6976a95b2f73b58644505812b2c12d6d",
        "per_page": 100,
    }

    all_products = []
    for page in range(1, 3):  # 10 pages x 100 products/page = 1000 products
        params['page'] = page
        response = requests.get(product_url, params=params)
        products = response.json()
        if not products:
            break
        all_products.extend(products)

    total_products = len(all_products)
    for index, product in enumerate(all_products, start=1):
        product_instance, created = Product.objects.get_or_create(product_id=product['id'], defaults=build_product_data(product))
        
        if created and product['type'] == 'variable':
            variation_url = base_url + f"products/{product['id']}/variations"
            variation_params = {
                "consumer_key": params["consumer_key"],
                "consumer_secret": params["consumer_secret"]
            }
            variations_response = requests.get(variation_url, params=variation_params)
            variations = variations_response.json()
            
            for var_index, variation in enumerate(variations, start=1):
                variation_instance, var_created = Product.objects.get_or_create(product_id=variation['id'], defaults=build_product_data(product, product_type='variation', variation=variation))
                
                # Import meta data for variation
                for meta in variation.get('meta_data', []):
                    ProductMetaData.objects.update_or_create(
                        product=variation_instance,
                        key=meta['key'],
                        defaults={
                            'value': meta['value'],
                            'description': meta.get('description', '')
                        }
                    )
                    
                # Log progress for variations
                print(f"Importing Variation {var_index} for Product {index}")

        # Import meta data for product
        for meta in product.get('meta_data', []):
            ProductMetaData.objects.update_or_create(
                product=product_instance,
                key=meta['key'],
                defaults={
                    'value': meta['value'],
                    'description': meta.get('description', '')
                }
            )

        # Log to the console for main products:
        print(f"Product Import Progress: {index} out of {total_products}")

    print("Product Import Completed!")



def resync_existing_products():
    base_url = "https://www.c2kft.co.uk/wp-json/wc/v3/"
    product_url = base_url + "products"
    params = {
        "consumer_key": "ck_3f9848c65bd04057454cc23cf514d0e0abb5bf3a",
        "consumer_secret": "cs_d2eec78a6976a95b2f73b58644505812b2c12d6d",
        "per_page": 100,
    }

    variation_params = {
        "consumer_key": params["consumer_key"],
        "consumer_secret": params["consumer_secret"],
    }

    all_products = []
    for page in range(1, 3):
        params['page'] = page
        response = requests.get(product_url, params=params)
        products = response.json()
        if not products:
            break
        all_products.extend(products)

    for product in all_products:
        print(f"Fetched product: {product['id']} - {product['name']}")

        if Product.objects.filter(product_id=product['id']).exists():
            existing_product = Product.objects.get(product_id=product['id'])
            updated_data, updated_meta_data = build_product_data(product)
            for key, value in updated_data.items():
                setattr(existing_product, key, value)
            existing_product.save()

            # Update product meta data
            for meta in updated_meta_data:
                ProductMetaData.objects.update_or_create(
                    product=existing_product,
                    key=meta['key'],
                    defaults={
                        'value': meta['value'],
                        'description': meta.get('description', '')
                    }
                )

            if product['type'] == 'variable':
                variation_url = base_url + f"products/{product['id']}/variations"
                variations_response = requests.get(variation_url, params=variation_params)
                variations = variations_response.json()

                for variation in variations:
                    if Product.objects.filter(product_id=variation['id']).exists():
                        existing_variation = Product.objects.get(product_id=variation['id'])
                        updated_variation_data, updated_variation_meta_data = build_product_data(product, product_type='variation', variation=variation)
                        for key, value in updated_variation_data.items():
                            setattr(existing_variation, key, value)
                        existing_variation.save()

                        # Update variation meta data
                        for meta in updated_variation_meta_data:
                            ProductMetaData.objects.update_or_create(
                                product=existing_variation,
                                key=meta['key'],
                                defaults={
                                    'value': meta['value'],
                                    'description': meta.get('description', '')
                                }
                            )

                        print(f"Updated variation {variation['id']} of product {product['id']}")
                    else:
                        print(f"Variation {variation['id']} not found in the database.")

    print("Resync Completed!")


def get_live_data(product_ids):
    # WooCommerce API Configuration
    base_url = "https://www.c2kft.co.uk/wp-json/wc/v3/"
    params = {
        "consumer_key": "ck_3f9848c65bd04057454cc23cf514d0e0abb5bf3a",
        "consumer_secret": "cs_d2eec78a6976a95b2f73b58644505812b2c12d6d",
        "include": ",".join(map(str, product_ids))
    }
    
    product_url = base_url + "products"
    response = requests.get(product_url, params=params)
    products_data = response.json()
    
    # Collect all the product IDs that are of type 'variable'
    variable_product_ids = [product['id'] for product in products_data if product.get('type') == 'variable']

    # For each variable product, fetch its variations and merge with the main product data
    for var_product_id in variable_product_ids:
        variations_url = f"{product_url}/{var_product_id}/variations"
        variations_response = requests.get(variations_url, params=params)
        variations_data = variations_response.json()
        products_data.extend(variations_data)  # Merge variations data with main products data

    # Convert the list of products (excluding those of type 'variable') into a dictionary with product_id as the key
    return {product['id']: product for product in products_data if product.get('type') != 'variable'}



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
    resync_existing_products()
    print(request, "Products resynced successfully!")
    return redirect('display_products')

def get_progress(request):
    progress = request.session.get('progress', "Starting import...")
    return JsonResponse({'progress': progress})


def product_page(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    metadata = product.meta_data.all()
    return render(request, 'products.html', {'product': product, 'metadata': metadata})



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



