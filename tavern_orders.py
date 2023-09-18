import requests
import json

BASE_URL = "https://thetackletavern.co.uk/wp-json/wc/v3/"
WC_CONSUMER_KEY = "ck_033584debafe468c9b441298a89c21a4d499cf3e"
WC_CONSUMER_SECRET = "cs_84b7b046fbeda0095b20f84e122c2dce2ca7a5d3"

def get_recent_orders():
    endpoint = BASE_URL + "orders"
    params = {
        "consumer_key": WC_CONSUMER_KEY,
        "consumer_secret": WC_CONSUMER_SECRET,
        "per_page": 10,   # get the latest 10 orders
        "orderby": "date",
        "order": "desc",
        "status": "completed"
    }

    response = requests.get(endpoint, params=params)
    orders = response.json()

    return orders

def print_order_data(orders):
    for order in orders:
        print(f"Order ID: {order['id']}")
        print("Order Data:")
        print(json.dumps(order, indent=4, sort_keys=True)) # This will print the order data in a formatted manner
        print("---------------------------")

if __name__ == "__main__":
    orders = get_recent_orders()
    print_order_data(orders)
