import json
import requests
from bs4 import BeautifulSoup


url = 'https://bikroy.com/en/ad/toyota-harrier-promet-octane-black-2020-for-sale-dhaka'

def get_ad_details(url):
    car_details = {
        'url': url,
        'year_of_production': None,
        'version': None,
        'price': None,
        'images': None,
        'title': None,
        'trim': None,
        'transmission': None,
        'registration_year': None,
        'fuel_type': None,
        'kilometers_driven': None,
        'model': None,
        'condition': None,
        'body_type': None,
        'engine_capacity': None,
        'posted_on': None,
        'seller_name': None,
        'contact': None
    }
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    script_tag = soup.find('script', text=lambda t: t and 'window.initialData' in t)

    start_index = script_tag.text.find('window.initialData = ') + len('window.initialData = ')
    end_index = len(script_tag.text) - 1

    json_data = script_tag.text[start_index:end_index]
    data = json.loads(json_data)

    adDetails = data.get('adDetail', {}).get('data', {}).get('ad', {})

    properties = adDetails.get('properties', [])
    car_details['images'] = adDetails.get('images', []).get('meta', [])
    car_details['title'] = adDetails.get('title')
    car_details['contact'] = adDetails.get('contactCard', {}).get('phoneNumbers', [])
    car_details['price'] = adDetails.get('money', {}).get('amount')
    car_details['seller_name'] = adDetails.get('shop', {}).get('name')
    car_details['posted_on'] = adDetails.get('adDate')
    for item in properties:
        if item['label'] == 'Year of Manufacture':
            car_details['year_of_production'] = item['value']
        elif item['label'] == 'Trim / Edition':
            car_details['version'] = item['value']
        elif item['label'] == 'Fuel type':
            car_details['fuel_type'] = item['value']
        elif item['label'] == 'Kilometers run':
            car_details['kilometers_driven'] = item['value']
        elif item['label'] == 'Model':
            car_details['model'] = item['value']
        elif item['label'] == 'Condition':
            car_details['condition'] = item['value']
        elif item['label'] == 'Transmission':
            car_details['transmission'] = item['value']
        elif item['label'] == 'Body type':
            car_details['body_type'] = item['value']
        elif item['label'] == 'Engine capacity':
            car_details['engine_capacity'] = item['value']
    return car_details


