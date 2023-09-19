from celery import shared_task
from products.models import Product, ProductMetaData
import requests, json
from django.db import transaction, IntegrityError
from products.sync import build_product_data


def load_credentials(filename="creds.json"):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

credentials = load_credentials()

WC_CONSUMER_KEY = credentials["WC_CONSUMER_KEY"]
WC_CONSUMER_SECRET = credentials["WC_CONSUMER_SECRET"]
BASE_URL = credentials["BASE_URL"]
PER_PAGE = 100

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
        'variations': str(product.get('variations', []))
    }

    # Extract meta data
    meta_data_list = product.get('meta_data', [])

    if product_type == 'variation' and variation:
        slug_base = product['slug']
        variation_slug = f"{slug_base}-{variation['id']}"
        data.update({
            'slug': variation_slug
        })
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


@shared_task
def import_new_products_task():
    product_url = BASE_URL + "products"
    params = {
        "consumer_key": WC_CONSUMER_KEY,
        "consumer_secret": WC_CONSUMER_SECRET,
        "per_page": PER_PAGE,
    }

    # Fetch the first page to get the total number of pages
    response = requests.get(product_url, params=params)
    total_pages = int(response.headers.get('X-WP-TotalPages', 1))

    for page in range(1, total_pages + 1):
        params['page'] = page
        response = requests.get(product_url, params=params)
        all_products = response.json()
        total_products = len(all_products)

        for index, product in enumerate(all_products, start=1):
            # Check if the product already exists in the database
            if Product.objects.filter(product_id=product['id']).exists():
                print(f"Product ID {product['id']} already exists. Skipping.")
                continue

            product_data, _ = build_product_data(product)
            
            # Attempt to create or update the product
            try:
                with transaction.atomic():
                    product_instance, created = Product.objects.update_or_create(product_id=product['id'], defaults=product_data)
                    
                    # Save meta data for the main product
                    for meta in product.get('meta_data', []):
                        try:
                            ProductMetaData.objects.update_or_create(
                                product=product_instance,
                                key=meta['key'],
                                defaults={
                                    'value': meta['value'],
                                    'description': meta.get('description', '')
                                }
                            )
                        except Exception as e:
                            print(f"Error with Meta Key '{meta['key']}' for Product ID {product['id']}: {str(e)}")
                            print(f"Meta Value: {meta['value']}")  # This line will print the value causing the issue
                    
            except IntegrityError as e:
                print(f"Integrity Error with Product ID {product['id']}: {str(e)}")
                continue
            except Exception as e:
                print(f"General Error with Product ID {product['id']}: {str(e)}")
                continue

            if created and product['type'] == 'variable':
                variation_url = BASE_URL + f"products/{product['id']}/variations"
                variation_params = {
                    "consumer_key": params["consumer_key"],
                    "consumer_secret": params["consumer_secret"]
                }
                variations_response = requests.get(variation_url, params=variation_params)
                variations = variations_response.json()
                
                for var_index, variation in enumerate(variations, start=1):
                    variation_data, _ = build_product_data(product, product_type='variation', variation=variation)
                    
                    # Attempt to create or update the variation
                    try:
                        with transaction.atomic():
                            variation_instance, var_created = Product.objects.update_or_create(product_id=variation['id'], defaults=variation_data)
                            
                            # Save meta data for the variation
                            for meta in variation.get('meta_data', []):
                                try:
                                    ProductMetaData.objects.update_or_create(
                                        product=variation_instance,
                                        key=meta['key'],
                                        defaults={
                                            'value': meta['value'],
                                            'description': meta.get('description', '')
                                        }
                                    )
                                except Exception as e:
                                    print(f"Error with Meta Key '{meta['key']}' for Variation ID {variation['id']} (Product ID {product['id']}): {str(e)}")
                                    print(f"Meta Value: {meta['value']}")  # This line will print the value causing the issue
                            
                    except IntegrityError as e:
                        print(f"Integrity Error with Variation ID {variation['id']} for Product ID {product['id']}: {str(e)}")
                        continue
                    except Exception as e:
                        print(f"General Error with Variation ID {variation['id']} for Product ID {product['id']}: {str(e)}")
                        continue

                    print(f"Imported Variation {var_index}/{len(variations)} for Product {index}/{total_products}")
                    
            print(f"Product Import Progress for Page {page}: {index}/{total_products}")
        print(f"Finished importing products from page {page}/{total_pages}")
