import requests

def fetch_product_details(product_id):
    base_url = "https://www.c2kft.co.uk/wp-json/wc/v3/"
    product_url = base_url + f"products/{product_id}"
    params = {
        "consumer_key": "ck_3f9848c65bd04057454cc23cf514d0e0abb5bf3a",
        "consumer_secret": "cs_d2eec78a6976a95b2f73b58644505812b2c12d6d",
    }

    response = requests.get(product_url, params=params)
    product = response.json()

    # Return the entire product details
    return product

# Fetch product details for product ID 142805
product_details = fetch_product_details(144823)

# Print the length of each data field
for key, value in product_details.items():
    print(f"Key: {key}, Value Length: {len(str(value))}")

    # If you want to see the actual value, uncomment the line below:
    # print(f"Key: {key}, Value: {value}")
