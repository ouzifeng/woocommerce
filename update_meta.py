import requests

# WooCommerce API Configuration
base_url = "https://www.c2kft.co.uk/wp-json/wc/v3/"
product_id = 144836
product_url = f"{base_url}products/{product_id}"

params = {
    "consumer_key": "ck_3f9848c65bd04057454cc23cf514d0e0abb5bf3a",
    "consumer_secret": "cs_d2eec78a6976a95b2f73b58644505812b2c12d6d"
}

# Fetch the current product data
response = requests.get(product_url, params=params)
product_data = response.json()

# Update the desired metadata value
for meta in product_data['meta_data']:
    if meta['key'] == '_yoast_wpseo_title':
        meta['value'] = 'club fishing tackle'
        break

# Update the product with the new metadata
updated_data = {
    'meta_data': product_data['meta_data']
}
response = requests.put(product_url, params=params, json=updated_data)

if response.status_code == 200:
    print("Metadata updated successfully!")
else:
    print(f"Failed to update metadata. Status code: {response.status_code}. Error: {response.text}")
