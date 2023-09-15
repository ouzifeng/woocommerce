import requests, os
import json
from .models import (Order, BillingProperties, ShippingProperties, 
                    OrderMetaData, CouponLines, Refunds, Taxes, OrderItem)
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from products.models import Product


WC_CONSUMER_KEY = 'ck_3f9848c65bd04057454cc23cf514d0e0abb5bf3a'
WC_CONSUMER_SECRET = 'cs_d2eec78a6976a95b2f73b58644505812b2c12d6d'
BASE_URL = 'https://www.c2kft.co.uk/wp-json/wc/v3/'
PER_PAGE = '10'


def import_orders_from_woocommerce():
    endpoint = BASE_URL + "orders"
    params = {
        "consumer_key": WC_CONSUMER_KEY,
        "consumer_secret": WC_CONSUMER_SECRET,
        "per_page": PER_PAGE,
    }

    # Make the request
    response = requests.get(endpoint, params=params)

    if response.status_code != 200:
        print("Error fetching orders:", response.content)
        return

    orders_data = response.json()

    for order_data in orders_data:
        aware_date_created = timezone.make_aware(datetime.strptime(order_data['date_created'], '%Y-%m-%dT%H:%M:%S'))
        aware_date_modified = timezone.make_aware(datetime.strptime(order_data['date_modified'], '%Y-%m-%dT%H:%M:%S'))

        # Create or update an Order instance
        order, created = Order.objects.update_or_create(
            order_id=order_data['id'],  # Using 'order_id' to map to WooCommerce's order ID
            defaults={
                'created_via': order_data['created_via'],
                'version': order_data['version'],
                'status': order_data['status'],
                'currency': order_data['currency'],
                'date_created': aware_date_created,
                'date_modified': aware_date_modified,
                'discount_total': Decimal(order_data['discount_total']),
                'discount_tax': Decimal(order_data['discount_tax']),
                'shipping_total': Decimal(order_data['shipping_total']),
                'shipping_tax': Decimal(order_data['shipping_tax']),
                'cart_tax': Decimal(order_data['cart_tax']),
                'total': Decimal(order_data['total']),
                'total_tax': Decimal(order_data['total_tax'])
            }
        )

        # Create or update BillingProperties
        billing_data = order_data['billing']
        billing, _ = BillingProperties.objects.update_or_create(
            order=order,
            defaults={
                'first_name': billing_data['first_name'],
                'last_name': billing_data['last_name'],
                'address_1': billing_data['address_1'],
                'address_2': billing_data['address_2'],
                'city': billing_data['city'],
                'postcode': billing_data['postcode'],
                'country': billing_data['country'],
                'email': billing_data['email'],
                'phone': billing_data['phone']
            }
        )
        order.billing = billing

        # Create or update ShippingProperties
        shipping_data = order_data['shipping']
        shipping, _ = ShippingProperties.objects.update_or_create(
            order=order,
            defaults={
                'first_name': shipping_data['first_name'],
                'last_name': shipping_data['last_name'],
                'address_1': shipping_data['address_1'],
                'address_2': shipping_data['address_2'],
                'city': shipping_data['city'],
                'postcode': shipping_data['postcode'],
                'country': shipping_data['country']
            }
        )
        order.shipping = shipping

        # Meta data
        for meta in order_data['meta_data']:
            OrderMetaData.objects.update_or_create(
                order=order,
                key=meta['key'],
                defaults={
                    'value': meta['value']
                }
            )

        # Coupon lines
        for coupon in order_data['coupon_lines']:
            CouponLines.objects.update_or_create(
                order=order,
                code=coupon['code'],
                defaults={
                    'discount': coupon['discount'],
                    'discount_tax': coupon['discount_tax']
                }
            )

        # Refunds
        for refund in order_data['refunds']:
            Refunds.objects.update_or_create(
                order=order,
                reason=refund['reason'],
                defaults={
                    'amount': refund['amount'],
                    'refunded_by': refund['refunded_by'],
                    'refund_id': refund['id']
                }
            )

        # Taxes
        for tax in order_data['tax_lines']:
            Taxes.objects.update_or_create(
                order=order,
                rate_code=tax['rate_code'],
                defaults={
                    'rate_id': tax['rate_id'],
                    'label': tax['label'],
                    'compound': tax['compound'],
                    'tax_total': tax['tax_total'],
                    'shipping_tax_total': tax['shipping_tax_total']
                }
            )
            
        for item in order_data['line_items']:
            product_id = item['product_id']
            quantity = item['quantity']
            price = item['price']

            # Assuming the Product model has an ID that corresponds to product_id from the API
            try:
                product = Product.objects.get(product_id=product_id)
                
                # Create or update the OrderItem
                OrderItem.objects.update_or_create(
                    order=order,
                    product=product,
                    defaults={
                        'quantity': quantity,
                        'price': price
                    }
                )
                
            except Product.DoesNotExist:
                # You can log this error or even save it to some error log in your DB.
                print(f"Product with ID {product_id} does not exist. Skipping order item.")
   

        # Save the order to ensure all relations are set correctly.
        order.save()

def display_orders(request):
    all_orders = Order.objects.all().order_by('-date_created')  # Displaying the latest orders first
    paginator = Paginator(all_orders, 10)  # Show 10 orders per page

    page_number = request.GET.get('page')
    paginated_orders = paginator.get_page(page_number)

    return render(request, 'orders_table.html', {'orders': paginated_orders})

def import_orders_view(request):
    import_orders_from_woocommerce()
    # Assuming you have a view called 'display_orders' to show all orders
    return redirect('display_orders')

def order_details(request, order_id):
    # Fetch the order based on the provided order ID
    order = get_object_or_404(Order, order_id=order_id)
    
    # Render the order details template with the order object
    return render(request, 'order_page.html', {'order': order})