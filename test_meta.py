import requests

base_url = "https://www.c2kft.co.uk/wp-json/wc/v3/"
product_id = 144836
product_url = f"{base_url}products/{product_id}"

params = {
    "consumer_key": "ck_3f9848c65bd04057454cc23cf514d0e0abb5bf3a",
    "consumer_secret": "cs_d2eec78a6976a95b2f73b58644505812b2c12d6d"
}

response = requests.get(product_url, params=params)

if response.status_code == 200:
    product_data = response.json()
    meta_data = product_data.get('meta_data', [])
    print(meta_data)
else:
    print(f"Failed to fetch product data. Status code: {response.status_code}")
