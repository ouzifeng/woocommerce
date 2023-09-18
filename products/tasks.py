from celery import shared_task
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductMetaData
import requests,json
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from decimal import Decimal
from django.db.utils import IntegrityError
from django.db import transaction
import os

def load_credentials(filename="creds.json"):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

credentials = load_credentials()

WC_CONSUMER_KEY = credentials["WC_CONSUMER_KEY"]
WC_CONSUMER_SECRET = credentials["WC_CONSUMER_SECRET"]
BASE_URL = credentials["BASE_URL"]
PER_PAGE = 100


@shared_task
def import_new_products_task():
    product_url = BASE_URL + "products"
    params = {
        "consumer_key": WC_CONSUMER_KEY,
        "consumer_secret": WC_CONSUMER_SECRET,
        "per_page": PER_PAGE,
    }

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
                
        print(f"Product Import Progress: {index}/{total_products}")

@shared_task        
def resync_existing_products_task():
    product_url = BASE_URL + "products"
    params = {
        "consumer_key": WC_CONSUMER_KEY,
        "consumer_secret": WC_CONSUMER_SECRET,
        "per_page": PER_PAGE,
    }

    response = requests.get(product_url, params=params)
    all_products = response.json()
    total_products = len(all_products)

    for index, product in enumerate(all_products, start=1):
        product_data, _ = build_product_data(product)
        
        # Attempt to create or update the main product data
        try:
            product_instance, created = Product.objects.update_or_create(product_id=product['id'], defaults=product_data)
            if created:
                print(f"Imported New Product ID {product['id']}")
            else:
                print(f"Updated Product ID {product['id']}")
        except IntegrityError as e:
            print(f"Integrity Error with Product ID {product['id']}: {str(e)}")
            continue
        except Exception as e:
            print(f"General Error with Product ID {product['id']}: {str(e)}")
            continue

        # Handle variations if the product type is variable
        if product['type'] == 'variable':
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
                    variation_instance, var_created = Product.objects.update_or_create(product_id=variation['id'], defaults=variation_data)
                    if var_created:
                        print(f"Imported New Variation ID {variation['id']} for Product ID {product['id']}")
                    else:
                        print(f"Updated Variation ID {variation['id']} for Product ID {product['id']}")
                except IntegrityError as e:
                    print(f"Integrity Error with Variation ID {variation['id']} for Product ID {product['id']}: {str(e)}")
                    continue
                except Exception as e:
                    print(f"General Error with Variation ID {variation['id']} for Product ID {product['id']}: {str(e)}")
                    continue
                
                print(f"Handled Variation {var_index}/{len(variations)} for Product {index}/{total_products}")

        print(f"Product Handling Progress: {index}/{total_products}")

    print("Resync Completed!")        