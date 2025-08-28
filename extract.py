import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import random

class CarDetailsExtractor:
    """
    Extracts car details from Bikroy.com using JavaScript data extraction
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_from_bikroy(self, url):
        """
        Extract car details from Bikroy.com using JavaScript data
        """
        try:
            print(f"🔍 Extracting from: {url}")
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the script tag containing window.initialData
            script_tag = soup.find('script', string=lambda t: t and 'window.initialData' in t)
            
            if not script_tag:
                print("❌ Could not find window.initialData script")
                return None
            
            # Extract JSON data from script
            script_text = script_tag.string
            start_index = script_text.find('window.initialData = ') + len('window.initialData = ')
            
            # Find the end of the JSON object by counting braces
            brace_count = 0
            end_index = start_index
            
            for i, char in enumerate(script_text[start_index:], start_index):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_index = i + 1
                        break
            
            json_data = script_text[start_index:end_index].strip()
            print(f"🔍 Found JSON data length: {len(json_data)}")
            
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"🔍 JSON start: {json_data[:100]}...")
                print(f"🔍 JSON end: ...{json_data[-100:]}")
                return None
            
            # Extract ad details
            adDetails = data.get('adDetail', {}).get('data', {}).get('ad', {})
            
            # Initialize car details structure
            car_details = {
                'url': url,
                'year_of_production': None,
                'version': None,
                'price': None,
                'images': [],
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
                'contact': [],
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract basic information
            raw_images = adDetails.get('images', {}).get('meta', [])
            car_details['images'] = []
            
            # Process images and append size parameters
            for img in raw_images:
                if isinstance(img, dict) and 'src' in img:
                    # Append size parameters to image URL
                    base_url = img['src']
                    if not base_url.endswith('/620/466/fitted.jpg'):
                        if base_url.endswith('/'):
                            base_url = base_url[:-1]  # Remove trailing slash
                        base_url += '/620/466/fitted.jpg'
                    
                    car_details['images'].append({
                        'src': base_url,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            
            car_details['title'] = adDetails.get('title')
            car_details['contact'] = adDetails.get('contactCard', {}).get('phoneNumbers', [])
            car_details['price'] = adDetails.get('money', {}).get('amount')
            car_details['seller_name'] = adDetails.get('shop', {}).get('name')
            car_details['posted_on'] = adDetails.get('adDate')
            
            # Extract properties
            properties = adDetails.get('properties', [])
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
            
            # Format price for display
            if car_details['price']:
                try:
                    price_num = int(car_details['price'])
                    car_details['price'] = f"Tk {price_num:,}"
                except (ValueError, TypeError):
                    # Remove any existing Tk prefix
                    price_str = str(car_details['price']).replace('Tk', '').strip()
                    car_details['price'] = f"Tk {price_str}"
            
            print(f"✅ Extracted: {car_details['title']}")
            print(f"💰 Price: {car_details['price']}")
            print(f"🚗 Model: {car_details['model']}")
            print(f"📅 Year: {car_details['year_of_production']}")
            print(f"🖼️  Images found: {len(car_details['images'])}")
            print(f"📞 Contact numbers: {len(car_details['contact'])}")
            
            return car_details
            
        except Exception as e:
            print(f"❌ Error extracting from {url}: {e}")
            return None
    
    def extract_from_general_site(self, url):
        """
        Extract car details from general websites (fallback method)
        """
        try:
            print(f"🔍 Extracting from general site: {url}")
            
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            car_details = {
                'url': url,
                'title': None,
                'price': None,
                'images': [],
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Try to find title
            title_elem = soup.find('h1') or soup.find('h2') or soup.find('title')
            if title_elem:
                car_details['title'] = title_elem.get_text(strip=True)
            
            # Try to find price
            price_elem = soup.find(string=re.compile(r'[\$€£₹]\s*[\d,]+|[\d,]+\s*[\$€£₹]|Tk\s*[\d,]+'))
            if price_elem:
                car_details['price'] = price_elem.strip()
            
            # Try to find images
            img_elements = soup.find_all('img')
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src and any(keyword in src.lower() for keyword in ['car', 'vehicle', 'auto', 'jpg', 'jpeg', 'png']):
                    if 'logo' not in src.lower() and 'icon' not in src.lower():
                        car_details['images'].append({
                            'src': src,
                            'alt': img.get('alt', ''),
                            'title': img.get('title', '')
                        })
            
            print(f"✅ Extracted: {car_details['title']}")
            print(f"💰 Price: {car_details['price']}")
            print(f"🖼️  Images found: {len(car_details['images'])}")
            
            return car_details
            
        except Exception as e:
            print(f"❌ Error extracting from {url}: {e}")
            return None
    
    def extract_car_details(self, url):
        """
        Main extraction method that determines the site type and extracts accordingly
        """
        domain = urlparse(url).netloc.lower()
        
        if 'bikroy' in domain:
            return self.extract_from_bikroy(url)
        else:
            return self.extract_from_general_site(url)
    
    def save_to_json(self, car_data, filename='extracted_car_details.json'):
        """
        Save extracted car details to JSON file
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(car_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving to {filename}: {e}")
            return False
    
    def extract_multiple_urls(self, urls):
        """
        Extract car details from multiple URLs
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n📋 Processing URL {i}/{len(urls)}")
            car_data = self.extract_car_details(url)
            if car_data:
                results.append(car_data)
            
            # Be respectful with delays
            if i < len(urls):
                delay = random.uniform(2, 5)
                print(f"⏳ Waiting {delay:.1f} seconds...")
                time.sleep(delay)
        
        return results

def main():
    """
    Main function for testing and demonstration
    """
    extractor = CarDetailsExtractor()
    
    # Example URLs to extract from
    example_urls = [
        "https://bikroy.com/en/ad/toyota-premio-f-2005-for-sale-dhaka-2175",
        # Add more URLs here
    ]
    
    print("🚗 Car Details Extractor")
    print("=" * 50)
    
    if len(example_urls) > 1:
        print("📋 Extracting from multiple URLs...")
        results = extractor.extract_multiple_urls(example_urls)
        
        if results:
            # Save all results
            extractor.save_to_json(results, 'extracted_cars.json')
            
            # Print summary
            print(f"\n📊 Extraction Summary:")
            print(f"✅ Successful: {len(results)}")
            print(f"❌ Failed: {len(example_urls) - len(results)}")
    else:
        print("🔍 Single URL extraction...")
        url = example_urls[0] if example_urls else input("Enter URL to extract from: ")
        
        if url:
            car_data = extractor.extract_car_details(url)
            if car_data:
                extractor.save_to_json(car_data, 'extracted_car_details.json')
            else:
                print("❌ Extraction failed")

if __name__ == "__main__":
    main()
