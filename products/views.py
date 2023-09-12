from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
import requests
import time
from django.http import JsonResponse
from django.core.paginator import Paginator

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
        'images': product['images'][0]['src'] if product.get('images', []) else '',
        'attributes': str(product.get('attributes', [])),
        'default_attributes': str(product.get('default_attributes', [])),
        'variations': str(product.get('variations', []))
    }

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

    return data

def fetch_products_from_woocommerce():
    base_url = "https://www.c2kft.co.uk/wp-json/wc/v3/"
    product_url = base_url + "products"
    params = {
        "consumer_key": "ck_3f9848c65bd04057454cc23cf514d0e0abb5bf3a",
        "consumer_secret": "cs_d2eec78a6976a95b2f73b58644505812b2c12d6d",
        "per_page": 100,
        "page": 1
    }
    max_retries = 3
    retries = 0
    fetched = False

    while retries < max_retries and not fetched:
        response = requests.get(product_url, params=params)
        
        if response.status_code == 200:
            products = response.json()
            
            if not products:
                return

            for product in products:
                product_data = build_product_data(product)
                Product.objects.create(**product_data)

                # If the product is a variable product, fetch its variations
                if product['type'] == 'variable':
                    variation_url = base_url + f"products/{product['id']}/variations"
                    variations_response = requests.get(variation_url, params=params)
                    variations = variations_response.json()
                    
                    for variation in variations:
                        variation_data = build_product_data(product, product_type='variation', variation=variation)
                        Product.objects.create(**variation_data)

            fetched = True  

        else:
            retries += 1
            time.sleep(5)

    if not fetched:
        print(f"Failed to fetch products after {max_retries} retries.")

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
        if not Product.objects.filter(product_id=product['id']).exists():
            product_data = build_product_data(product)
            Product.objects.create(**product_data)

            if product['type'] == 'variable':
                variation_url = base_url + f"products/{product['id']}/variations"
                # Use a separate params dictionary for variations
                variation_params = {
                    "consumer_key": params["consumer_key"],
                    "consumer_secret": params["consumer_secret"]
                }
                variations_response = requests.get(variation_url, params=variation_params)
                variations = variations_response.json()
                
                for var_index, variation in enumerate(variations, start=1):
                    if not Product.objects.filter(product_id=variation['id']).exists():
                        variation_data = build_product_data(product, product_type='variation', variation=variation)
                        Product.objects.create(**variation_data)
                    
                    # Log progress for variations
                    print(f"Importing Variation {var_index} for Product {index}")

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
    
    # Separate params for variations to avoid any interference
    variation_params = {
        "consumer_key": params["consumer_key"],
        "consumer_secret": params["consumer_secret"],
    }

    all_products = []
    for page in range(1, 3):  # Fetching 200 products
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
            updated_data = build_product_data(product)
            for key, value in updated_data.items():
                setattr(existing_product, key, value)
            existing_product.save()
            print(f"Updated product {product['id']}")

        if product['type'] == 'variable':
            print(f"Fetching variations for product {product['id']}")
            variation_url = base_url + f"products/{product['id']}/variations"
            variations_response = requests.get(variation_url, params=variation_params)
            variations = variations_response.json()

            for variation in variations:
                print(f"Found variation: {variation['id']}")
                if Product.objects.filter(product_id=variation['id']).exists():
                    existing_variation = Product.objects.get(product_id=variation['id'])
                    updated_variation_data = build_product_data(product, product_type='variation', variation=variation)
                    for key, value in updated_variation_data.items():
                        setattr(existing_variation, key, value)
                    existing_variation.save()
                    print(f"Updated variation {variation['id']} of product {product['id']}")
                else:
                    print(f"Variation {variation['id']} not found in the database.")

    print("Resync Completed!")





def display_products(request):
    products = Product.objects.all()
    return render(request, 'products_table.html', {'products': products})

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

def display_products(request):
    all_products = Product.objects.all().order_by('name', 'product_id')
    paginator = Paginator(all_products, 10)  # Show 25 products per page

    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'products_table.html', {'products': products})

def product_page(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    return render(request, 'products.html', {'product': product})
