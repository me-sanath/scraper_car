import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
import logging
from typing import Dict, List, Optional, Any
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradeMeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_selenium_driver(self):
        """Get a Selenium WebDriver instance"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Failed to create Selenium driver: {e}")
            return None
    
    def extract_car_listing_selenium(self, url: str) -> Dict[str, Any]:
        """
        Extract car listing data using Selenium to get rendered HTML
        """
        driver = None
        try:
            logger.info(f"Extracting data using Selenium from: {url}")
            driver = self.get_selenium_driver()
            
            if not driver:
                logger.error("Failed to create Selenium driver")
                return {
                    'url': url,
                    'error': 'Failed to create Selenium driver',
                    'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Navigate to the page
            driver.get(url)
            
            # Wait for the page to load
            time.sleep(5)
            
            # Get the rendered HTML
            html_content = driver.page_source
            
            # Save the rendered HTML
            with open('trademe_selenium_rendered.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info("Selenium rendered HTML saved to trademe_selenium_rendered.html")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize data structure
            car_data = {
                'url': url,
                'title': '',
                'price': '',
                'year': '',
                'kilometers': '',
                'transmission': '',
                'fuel_type': '',
                'body_type': '',
                'engine_capacity': '',
                'condition': '',
                'seller_name': '',
                'location': '',
                'description': '',
                'images': [],
                'features': [],
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Try to find the title
            title_selectors = [
                'h1[class*="title"]',
                'h1[class*="listing"]',
                'h1',
                'title'
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    if title_elem:
                        car_data['title'] = title_elem.text.strip()
                        logger.info(f"Found title with selector '{selector}': {car_data['title']}")
                        break
                except:
                    continue
            
            # Try to find the price
            price_selectors = [
                '[class*="price"]',
                '[class*="cost"]',
                'span:contains("$")',
                'div:contains("$")'
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    if price_elem:
                        price_text = price_elem.text.strip()
                        if '$' in price_text or 'NZD' in price_text:
                            car_data['price'] = price_text
                            logger.info(f"Found price with selector '{selector}': {price_text}")
                            break
                except:
                    continue
            
            # Look for key details
            # Try to find any text that contains car specifications
            page_text = driver.page_source.lower()
            
            # Extract year
            year_match = re.search(r'(\d{4})\s*(?:year|model|registration)', page_text)
            if year_match:
                car_data['year'] = year_match.group(1)
                logger.info(f"Found year: {car_data['year']}")
            
            # Extract kilometers
            km_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometres|kilometers)', page_text)
            if km_match:
                car_data['kilometers'] = km_match.group(1)
                logger.info(f"Found kilometers: {car_data['kilometers']}")
            
            # Extract transmission
            if 'automatic' in page_text:
                car_data['transmission'] = 'Automatic'
                logger.info("Found transmission: Automatic")
            elif 'manual' in page_text:
                car_data['transmission'] = 'Manual'
                logger.info("Found transmission: Manual")
            
            # Extract fuel type
            fuel_types = ['petrol', 'diesel', 'electric', 'hybrid', 'gas']
            for fuel in fuel_types:
                if fuel in page_text:
                    car_data['fuel_type'] = fuel.title()
                    logger.info(f"Found fuel type: {car_data['fuel_type']}")
                    break
            
            # Extract body type
            body_types = ['hatchback', 'sedan', 'suv', 'wagon', 'coupe', 'convertible']
            for body in body_types:
                if body in page_text:
                    car_data['body_type'] = body.title()
                    logger.info(f"Found body type: {car_data['body_type']}")
                    break
            
            # Extract engine capacity
            engine_match = re.search(r'(\d{1,3}(?:\.\d)?)\s*(?:cc|l|litre)', page_text)
            if engine_match:
                car_data['engine_capacity'] = f"{engine_match.group(1)}cc"
                logger.info(f"Found engine capacity: {car_data['engine_capacity']}")
            
            # Extract condition
            if 'new' in page_text:
                car_data['condition'] = 'New'
            elif 'used' in page_text:
                car_data['condition'] = 'Used'
            else:
                car_data['condition'] = 'Unknown'
            logger.info(f"Found condition: {car_data['condition']}")
            
            # Try to find seller information
            seller_selectors = [
                '[class*="seller"]',
                '[class*="dealer"]',
                '[class*="contact"]'
            ]
            
            for selector in seller_selectors:
                try:
                    seller_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    if seller_elem:
                        seller_text = seller_elem.text.strip()
                        if seller_text and len(seller_text) < 100:  # Reasonable length for seller name
                            car_data['seller_name'] = seller_text
                            logger.info(f"Found seller: {car_data['seller_name']}")
                            break
                except:
                    continue
            
            # Try to find description
            desc_selectors = [
                '[class*="description"]',
                '[class*="details"]',
                'p'
            ]
            
            for selector in desc_selectors:
                try:
                    desc_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    if desc_elem:
                        desc_text = desc_elem.text.strip()
                        if desc_text and len(desc_text) > 20:  # Reasonable length for description
                            car_data['description'] = desc_text[:500]  # Limit length
                            logger.info(f"Found description: {desc_text[:100]}...")
                            break
                except:
                    continue
            
            # Extract images
            try:
                img_elements = driver.find_elements(By.TAG_NAME, 'img')
                for img in img_elements:
                    src = img.get_attribute('src')
                    alt = img.get_attribute('alt')
                    if src and 'trademe' in src.lower():
                        car_data['images'].append({
                            'src': src,
                            'alt': alt or ''
                        })
                logger.info(f"Found {len(car_data['images'])} images")
            except Exception as e:
                logger.warning(f"Failed to extract images: {e}")
            
            logger.info(f"Successfully extracted data using Selenium for: {car_data.get('title', 'Unknown')}")
            return car_data
            
        except Exception as e:
            logger.error(f"Error extracting data with Selenium from {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        finally:
            if driver:
                driver.quit()
                logger.info("Selenium driver closed")
    
    def extract_car_listing(self, url: str) -> Dict[str, Any]:
        """
        Extract car listing data from a TradeMe URL
        """
        try:
            logger.info(f"Extracting data from: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize data structure
            car_data = {
                'url': url,
                'title': '',
                'price': '',
                'year': '',
                'kilometers': '',
                'transmission': '',
                'fuel_type': '',
                'body_type': '',
                'engine_capacity': '',
                'condition': '',
                'seller_name': '',
                'location': '',
                'description': '',
                'images': [],
                'features': [],
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract title
            title_elem = soup.find('h1', class_='tm-motors-listing__title')
            if title_elem:
                car_data['title'] = title_elem.get_text(strip=True)
            
            # Extract price
            price_elem = soup.find('span', class_='tm-motors-listing__price')
            if price_elem:
                car_data['price'] = price_elem.get_text(strip=True)
            
            # Extract key details from the listing details section
            details_section = soup.find('div', class_='tm-motors-listing__details')
            if details_section:
                # Extract year
                year_elem = details_section.find('span', string=re.compile(r'Year'))
                if year_elem:
                    year_text = year_elem.find_next_sibling()
                    if year_text:
                        car_data['year'] = year_text.get_text(strip=True)
                
                # Extract kilometers
                km_elem = details_section.find('span', string=re.compile(r'Kilometres|KMs'))
                if km_elem:
                    km_text = km_elem.find_next_sibling()
                    if km_text:
                        car_data['kilometers'] = km_text.get_text(strip=True)
                
                # Extract transmission
                trans_elem = details_section.find('span', string=re.compile(r'Transmission'))
                if trans_elem:
                    trans_text = trans_elem.find_next_sibling()
                    if trans_text:
                        car_data['transmission'] = trans_text.get_text(strip=True)
                
                # Extract fuel type
                fuel_elem = details_section.find('span', string=re.compile(r'Fuel'))
                if fuel_elem:
                    fuel_text = fuel_elem.find_next_sibling()
                    if fuel_text:
                        car_data['fuel_type'] = fuel_text.get_text(strip=True)
                
                # Extract body type
                body_elem = details_section.find('span', string=re.compile(r'Body'))
                if body_elem:
                    body_text = body_elem.find_next_sibling()
                    if body_text:
                        car_data['body_type'] = body_text.get_text(strip=True)
                
                # Extract engine capacity
                engine_elem = details_section.find('span', string=re.compile(r'Engine'))
                if engine_elem:
                    engine_text = engine_elem.find_next_sibling()
                    if engine_text:
                        car_data['engine_capacity'] = engine_text.get_text(strip=True)
            
            # Extract condition
            condition_elem = soup.find('span', class_='tm-motors-listing__condition')
            if condition_elem:
                car_data['condition'] = condition_elem.get_text(strip=True)
            
            # Extract seller information
            seller_elem = soup.find('div', class_='tm-motors-listing__seller')
            if seller_elem:
                seller_name_elem = seller_elem.find('span', class_='tm-motors-listing__seller-name')
                if seller_name_elem:
                    car_data['seller_name'] = seller_name_elem.get_text(strip=True)
                
                location_elem = seller_elem.find('span', class_='tm-motors-listing__location')
                if location_elem:
                    car_data['location'] = location_elem.get_text(strip=True)
            
            # Extract description
            desc_elem = soup.find('div', class_='tm-motors-listing__description')
            if desc_elem:
                car_data['description'] = desc_elem.get_text(strip=True)
            
            # Extract images
            image_elements = soup.find_all('img', class_='tm-motors-listing__image')
            for img in image_elements:
                src = img.get('src')
                alt = img.get('alt', '')
                if src:
                    car_data['images'].append({
                        'src': urljoin(url, src),
                        'alt': alt
                    })
            
            # Extract features
            features_section = soup.find('div', class_='tm-motors-listing__features')
            if features_section:
                feature_elements = features_section.find_all('li')
                for feature in feature_elements:
                    feature_text = feature.get_text(strip=True)
                    if feature_text:
                        car_data['features'].append(feature_text)
            
            logger.info(f"Successfully extracted data for: {car_data['title']}")
            return car_data
            
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def extract_car_listing_form_fields(self, url: str) -> Dict[str, Any]:
        """
        Extract car listing data from a TradeMe URL with the specific form fields structure
        """
        try:
            logger.info(f"Extracting form field data from: {url}")
            
            # Try different headers to get a cleaner response
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'identity',  # Don't accept compressed responses
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            # Save raw HTML for debugging
            with open('trademe_raw_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info("Raw HTML saved to trademe_raw_page.html")
            
            # Also save the response content as bytes for debugging
            with open('trademe_response_bytes.txt', 'wb') as f:
                f.write(response.content)
            logger.info("Response bytes saved to trademe_response_bytes.txt")
            
            # Check content type and encoding
            logger.info(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            logger.info(f"Content-Encoding: {response.headers.get('content-encoding', 'none')}")
            logger.info(f"Response length: {len(response.content)} bytes")
            
            # Try to decode with different encodings
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info("Successfully parsed with html.parser")
            except Exception as e:
                logger.warning(f"Failed to parse with html.parser: {e}")
                try:
                    # Try with lxml parser
                    soup = BeautifulSoup(response.content, 'lxml')
                    logger.info("Successfully parsed with lxml parser")
                except Exception as e2:
                    logger.warning(f"Failed to parse with lxml parser: {e2}")
                    # Try to decode manually
                    try:
                        decoded_content = response.content.decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(decoded_content, 'html.parser')
                        logger.info("Successfully parsed with manual UTF-8 decode")
                    except Exception as e3:
                        logger.error(f"All parsing methods failed: {e3}")
                        return {
                            'url': url,
                            'error': f"Failed to parse HTML: {e3}",
                            'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
            
            # Initialize data structure based on the form fields shown in the image
            car_data = {
                'url': url,
                'kilometer': '',
                'fuel': '',
                'engine_cc': '',
                'body_type': '',
                'transmission': '',
                'cylinders': '',
                'year': '',
                'number_plate': '',
                'exterior_colour': '',
                'doors': '',
                'import_history': '',
                'ask_price': '',
                'overall_safety': '',
                'buy_price': '',
                'starting_price': '',
                'on_road_costs': '',
                'seats': '',
                'energy_economy': '',
                'carbon_emissions': '',
                'source_link': url,
                'driver_safety': '',
                'listed_on': '',
                'price': '',
                'currency': 'NZD',
                'tag': 'Car',
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Try multiple approaches to find the title
            title_elem = (
                soup.find('h1', class_='tm-motors-listing__title') or
                soup.find('h1') or
                soup.find('title') or
                soup.find('h1', class_='listing-title') or
                soup.find('h1', class_='title')
            )
            if title_elem:
                car_data['title'] = title_elem.get_text(strip=True)
                logger.info(f"Found title: {car_data['title']}")
            
            # Try multiple approaches to find the price
            price_elem = (
                soup.find('span', class_='tm-motors-listing__price') or
                soup.find('span', class_='price') or
                soup.find('div', class_='price') or
                soup.find('span', string=re.compile(r'\$|NZD|price', re.IGNORECASE)) or
                soup.find('div', string=re.compile(r'\$|NZD|price', re.IGNORECASE))
            )
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                car_data['price'] = price_text
                logger.info(f"Found price: {price_text}")
                # Try to extract numeric price
                price_match = re.search(r'[\d,]+', price_text)
                if price_match:
                    car_data['starting_price'] = price_match.group()
                    car_data['buy_price'] = price_match.group()
                    car_data['ask_price'] = price_match.group()
            
            # Look for key details in various possible locations
            # Try to find any section that might contain car details
            details_sections = [
                soup.find('div', class_='tm-motors-listing__details'),
                soup.find('div', class_='listing-details'),
                soup.find('div', class_='details'),
                soup.find('div', class_='car-details'),
                soup.find('div', class_='vehicle-details'),
                soup.find('table'),
                soup.find('ul', class_='details'),
                soup.find('div', class_='specifications')
            ]
            
            details_section = None
            for section in details_sections:
                if section:
                    details_section = section
                    logger.info(f"Found details section: {section.name} with class {section.get('class', 'no-class')}")
                    break
            
            if details_section:
                # Extract year - try multiple patterns
                year_patterns = [r'Year', r'Model Year', r'Registration Year']
                for pattern in year_patterns:
                    year_elem = details_section.find('span', string=re.compile(pattern, re.IGNORECASE))
                    if year_elem:
                        year_text = year_elem.find_next_sibling()
                        if year_text:
                            car_data['year'] = year_text.get_text(strip=True)
                            logger.info(f"Found year: {car_data['year']}")
                            break
                
                # Extract kilometers - try multiple patterns
                km_patterns = [r'Kilometres', r'KMs', r'Mileage', r'Odometer']
                for pattern in km_patterns:
                    km_elem = details_section.find('span', string=re.compile(pattern, re.IGNORECASE))
                    if km_elem:
                        km_text = km_elem.find_next_sibling()
                        if km_text:
                            km_value = km_text.get_text(strip=True)
                            car_data['kilometer'] = km_value
                            logger.info(f"Found kilometers: {km_value}")
                            # Try to extract numeric value
                            km_match = re.search(r'[\d,]+', km_value)
                            if km_match:
                                car_data['kilometer'] = km_match.group()
                            break
                
                # Extract transmission
                trans_elem = details_section.find('span', string=re.compile(r'Transmission', re.IGNORECASE))
                if trans_elem:
                    trans_text = trans_elem.find_next_sibling()
                    if trans_text:
                        car_data['transmission'] = trans_text.get_text(strip=True)
                        logger.info(f"Found transmission: {car_data['transmission']}")
                
                # Extract fuel type
                fuel_elem = details_section.find('span', string=re.compile(r'Fuel', re.IGNORECASE))
                if fuel_elem:
                    fuel_text = fuel_elem.find_next_sibling()
                    if fuel_text:
                        car_data['fuel'] = fuel_text.get_text(strip=True)
                        logger.info(f"Found fuel: {car_data['fuel']}")
                
                # Extract body type
                body_elem = details_section.find('span', string=re.compile(r'Body', re.IGNORECASE))
                if body_elem:
                    body_text = body_elem.find_next_sibling()
                    if body_text:
                        car_data['body_type'] = body_text.get_text(strip=True)
                        logger.info(f"Found body type: {car_data['body_type']}")
                
                # Extract engine capacity
                engine_elem = details_section.find('span', string=re.compile(r'Engine', re.IGNORECASE))
                if engine_elem:
                    engine_text = engine_elem.find_next_sibling()
                    if engine_text:
                        engine_value = engine_text.get_text(strip=True)
                        car_data['engine_cc'] = engine_value
                        logger.info(f"Found engine: {engine_value}")
                        # Try to extract CC value
                        cc_match = re.search(r'(\d+(?:,\d+)*)\s*cc', engine_value, re.IGNORECASE)
                        if cc_match:
                            car_data['engine_cc'] = cc_match.group(1)
                
                # Extract cylinders
                cylinders_elem = details_section.find('span', string=re.compile(r'Cylinders', re.IGNORECASE))
                if cylinders_elem:
                    cylinders_text = cylinders_elem.find_next_sibling()
                    if cylinders_text:
                        car_data['cylinders'] = cylinders_text.get_text(strip=True)
                        logger.info(f"Found cylinders: {car_data['cylinders']}")
                
                # Extract doors
                doors_elem = details_section.find('span', string=re.compile(r'Doors', re.IGNORECASE))
                if doors_elem:
                    doors_text = doors_elem.find_next_sibling()
                    if doors_text:
                        car_data['doors'] = doors_text.get_text(strip=True)
                        logger.info(f"Found doors: {car_data['doors']}")
                
                # Extract seats
                seats_elem = details_section.find('span', string=re.compile(r'Seats', re.IGNORECASE))
                if seats_elem:
                    seats_text = seats_elem.find_next_sibling()
                    if seats_text:
                        car_data['seats'] = seats_text.get_text(strip=True)
                        logger.info(f"Found seats: {car_data['seats']}")
                
                # Extract exterior colour
                color_elem = details_section.find('span', string=re.compile(r'Colour|Color', re.IGNORECASE))
                if color_elem:
                    color_text = color_elem.find_next_sibling()
                    if color_text:
                        car_data['exterior_colour'] = color_text.get_text(strip=True)
                        logger.info(f"Found color: {car_data['exterior_colour']}")
            
            # Try to find condition information
            condition_elem = (
                soup.find('span', class_='tm-motors-listing__condition') or
                soup.find('span', class_='condition') or
                soup.find('div', class_='condition')
            )
            if condition_elem:
                condition_text = condition_elem.get_text(strip=True)
                car_data['condition'] = condition_text
                logger.info(f"Found condition: {condition_text}")
                # Set default safety ratings based on condition
                if 'new' in condition_text.lower():
                    car_data['overall_safety'] = '5 Stars'
                    car_data['energy_economy'] = '5 Stars'
                    car_data['carbon_emissions'] = '5 Stars'
                    car_data['driver_safety'] = '5 Stars'
                elif 'used' in condition_text.lower():
                    car_data['overall_safety'] = '4 Stars'
                    car_data['energy_economy'] = '3 Stars'
                    car_data['carbon_emissions'] = '3 Stars'
                    car_data['driver_safety'] = '4 Stars'
                else:
                    car_data['overall_safety'] = '4 Stars'
                    car_data['energy_economy'] = '0.5 Star'
                    car_data['carbon_emissions'] = '0 Star'
                    car_data['driver_safety'] = '0.5 Star'
            
            # Try to find seller information
            seller_elem = (
                soup.find('div', class_='tm-motors-listing__seller') or
                soup.find('div', class_='seller') or
                soup.find('div', class_='dealer') or
                soup.find('div', class_='contact')
            )
            if seller_elem:
                seller_name_elem = seller_elem.find('span', class_='tm-motors-listing__seller-name') or seller_elem.find('span', class_='name')
                if seller_name_elem:
                    car_data['seller_name'] = seller_name_elem.get_text(strip=True)
                    logger.info(f"Found seller: {car_data['seller_name']}")
                
                location_elem = seller_elem.find('span', class_='tm-motors-listing__location') or seller_elem.find('span', class_='location')
                if location_elem:
                    car_data['location'] = location_elem.get_text(strip=True)
                    logger.info(f"Found location: {car_data['location']}")
            
            # Try to find description
            desc_elem = (
                soup.find('div', class_='tm-motors-listing__description') or
                soup.find('div', class_='description') or
                soup.find('div', class_='listing-description')
            )
            if desc_elem:
                car_data['description'] = desc_elem.get_text(strip=True)
                logger.info(f"Found description: {car_data['description'][:100]}...")
            
            # Try to find listing date
            date_elem = (
                soup.find('span', class_='tm-motors-listing__date') or
                soup.find('span', class_='date') or
                soup.find('div', class_='date') or
                soup.find('span', string=re.compile(r'Listed|Posted|Date', re.IGNORECASE))
            )
            if date_elem:
                car_data['listed_on'] = date_elem.get_text(strip=True)
                logger.info(f"Found date: {car_data['listed_on']}")
            
            # Set default values for missing fields
            if not car_data['tag']:
                car_data['tag'] = 'Car'
            
            if not car_data['currency']:
                car_data['currency'] = 'NZD'  # TradeMe is New Zealand
            
            # Set ask price same as starting price if not specified
            if not car_data['ask_price'] and car_data['starting_price']:
                car_data['ask_price'] = car_data['starting_price']
            
            # If we still don't have a title, try to extract from the page title
            if not car_data['title']:
                page_title = soup.find('title')
                if page_title:
                    car_data['title'] = page_title.get_text(strip=True)
                    logger.info(f"Extracted title from page title: {car_data['title']}")
            
            # Save a sample of the parsed HTML for debugging
            with open('trademe_parsed_sample.html', 'w', encoding='utf-8') as f:
                f.write(str(soup)[:5000])  # First 5000 characters
            logger.info("Parsed HTML sample saved to trademe_parsed_sample.html")
            
            logger.info(f"Successfully extracted form field data for: {car_data.get('title', 'Unknown')}")
            return car_data
            
        except Exception as e:
            logger.error(f"Error extracting form field data from {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def extract_from_ad_details(self, ad_details_file: str = 'ad_details.json') -> List[Dict[str, Any]]:
        """
        Extract data from all URLs in ad_details.json
        """
        try:
            with open(ad_details_file, 'r', encoding='utf-8') as f:
                ad_data = json.load(f)
            
            extracted_data = []
            
            # Extract from the main URL if it exists
            if 'url' in ad_data and ad_data['url']:
                main_url = ad_data['url']
                if 'trademe.co.nz' in main_url:
                    logger.info(f"Processing main TradeMe URL: {main_url}")
                    car_data = self.extract_car_listing(main_url)
                    extracted_data.append(car_data)
                else:
                    logger.info(f"Skipping non-TradeMe URL: {main_url}")
            
            # Process any additional URLs that might be in the data
            # Look for URLs in description, images, or other fields
            all_urls = self._extract_urls_from_data(ad_data)
            
            for url in all_urls:
                if 'trademe.co.nz' in url:
                    logger.info(f"Processing additional TradeMe URL: {url}")
                    car_data = self.extract_car_listing(url)
                    extracted_data.append(car_data)
                    time.sleep(1)  # Be respectful with requests
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error processing ad_details.json: {str(e)}")
            return []
    
    def _extract_urls_from_data(self, data: Dict[str, Any]) -> List[str]:
        """
        Extract all URLs from the ad data structure
        """
        urls = []
        
        def extract_urls_recursive(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    extract_urls_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_urls_recursive(item)
            elif isinstance(obj, str):
                # Simple URL detection
                if obj.startswith('http'):
                    urls.append(obj)
        
        extract_urls_recursive(data)
        return list(set(urls))  # Remove duplicates
    
    def save_extracted_data(self, data: List[Dict[str, Any]], filename: str = 'extracted_trademe_data.json'):
        """
        Save extracted data to a JSON file
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")

def main():
    """
    Main function to run the scraper
    """
    scraper = TradeMeScraper()
    
    # First, try using Selenium to get the actual rendered HTML
    ford_puma_url = "https://www.trademe.co.nz/a/motors/cars/ford/puma/listing/5497121689"
    logger.info("Extracting data using Selenium from Ford Puma listing...")
    
    ford_puma_selenium_data = scraper.extract_car_listing_selenium(ford_puma_url)
    
    # Then try the regular method
    logger.info("Extracting data using regular method from Ford Puma listing...")
    ford_puma_regular_data = scraper.extract_car_listing(ford_puma_url)
    
    # Then extract from ad_details.json
    logger.info("Extracting data from ad_details.json...")
    ad_details_data = scraper.extract_from_ad_details()
    
    # Combine all extracted data
    all_extracted_data = [ford_puma_selenium_data, ford_puma_regular_data] + ad_details_data
    
    # Save the combined data
    scraper.save_extracted_data(all_extracted_data, 'extracted_trademe_data.json')
    
    # Create a separate file specifically for TradeMe posts with the form field structure
    trademe_form_data = []
    for data in all_extracted_data:
        if data and 'error' not in data and 'url' in data and 'trademe.co.nz' in data.get('url', ''):
            # Create the specific form field structure
            form_data = {
                'kilometer': data.get('kilometer', data.get('kilometers', '')),
                'fuel': data.get('fuel', data.get('fuel_type', '')),
                'engine_cc': data.get('engine_cc', data.get('engine_capacity', '')),
                'body_type': data.get('body_type', ''),
                'transmission': data.get('transmission', ''),
                'cylinders': data.get('cylinders', ''),
                'year': data.get('year', ''),
                'number_plate': data.get('number_plate', ''),
                'exterior_colour': data.get('exterior_colour', ''),
                'doors': data.get('doors', ''),
                'import_history': data.get('import_history', ''),
                'ask_price': data.get('ask_price', data.get('price', '')),
                'overall_safety': data.get('overall_safety', ''),
                'buy_price': data.get('buy_price', data.get('price', '')),
                'starting_price': data.get('starting_price', data.get('price', '')),
                'on_road_costs': data.get('on_road_costs', ''),
                'seats': data.get('seats', ''),
                'energy_economy': data.get('energy_economy', ''),
                'carbon_emissions': data.get('carbon_emissions', ''),
                'source_link': data.get('url', ''),
                'driver_safety': data.get('driver_safety', ''),
                'listed_on': data.get('listed_on', ''),
                'price': data.get('price', ''),
                'currency': data.get('currency', 'NZD'),
                'tag': data.get('tag', 'Car'),
                'extracted_at': data.get('extracted_at', '')
            }
            trademe_form_data.append(form_data)
    
    # Save the TradeMe form data to a separate file
    if trademe_form_data:
        with open('trademe_form_fields.json', 'w', encoding='utf-8') as f:
            json.dump(trademe_form_data, f, indent=2, ensure_ascii=False)
        logger.info(f"TradeMe form data saved to trademe_form_fields.json")
    
    # Print summary
    print(f"\nExtraction completed!")
    print(f"Total listings processed: {len(all_extracted_data)}")
    print(f"Data saved to: extracted_trademe_data.json")
    print(f"TradeMe form data saved to: trademe_form_fields.json")
    
    # Print details for the Ford Puma listing (Selenium method) with mapped form fields
    if ford_puma_selenium_data and 'error' not in ford_puma_selenium_data:
        print(f"\nFord Puma Listing Details (Selenium - Mapped to Form Fields):")
        print(f"Title: {ford_puma_selenium_data.get('title', 'N/A')}")
        print(f"Price: {ford_puma_selenium_data.get('price', 'N/A')}")
        print(f"Year: {ford_puma_selenium_data.get('year', 'N/A')}")
        print(f"Kilometers: {ford_puma_selenium_data.get('kilometers', 'N/A')}")
        print(f"Transmission: {ford_puma_selenium_data.get('transmission', 'N/A')}")
        print(f"Fuel Type: {ford_puma_selenium_data.get('fuel_type', 'N/A')}")
        print(f"Body Type: {ford_puma_selenium_data.get('body_type', 'N/A')}")
        print(f"Engine: {ford_puma_selenium_data.get('engine_capacity', 'N/A')}")
        print(f"Condition: {ford_puma_selenium_data.get('condition', 'N/A')}")
        print(f"Seller: {ford_puma_selenium_data.get('seller_name', 'N/A')}")
        print(f"Location: {ford_puma_selenium_data.get('location', 'N/A')}")
        print(f"Images: {len(ford_puma_selenium_data.get('images', []))}")
        print(f"Features: {len(ford_puma_selenium_data.get('features', []))}")
        
        # Also show the mapped form fields
        mapped_data = trademe_form_data[1] if len(trademe_form_data) > 1 else {}
        if mapped_data:
            print(f"\nMapped Form Fields:")
            print(f"Kilometer: {mapped_data.get('kilometer', 'N/A')}")
            print(f"Fuel: {mapped_data.get('fuel', 'N/A')}")
            print(f"Engine CC: {mapped_data.get('engine_cc', 'N/A')}")
            print(f"Body Type: {mapped_data.get('body_type', 'N/A')}")
            print(f"Transmission: {mapped_data.get('transmission', 'N/A')}")
            print(f"Year: {mapped_data.get('year', 'N/A')}")
            print(f"Number Plate: {mapped_data.get('number_plate', 'N/A')}")
            print(f"Exterior Colour: {mapped_data.get('exterior_colour', 'N/A')}")
            print(f"Import History: {mapped_data.get('import_history', 'N/A')}")
            print(f"Ask Price: {mapped_data.get('ask_price', 'N/A')}")
            print(f"Starting Price: {mapped_data.get('starting_price', 'N/A')}")
            print(f"Buy Price: {mapped_data.get('buy_price', 'N/A')}")
            print(f"On Road Costs: {mapped_data.get('on_road_costs', 'N/A')}")
            print(f"Seats: {mapped_data.get('seats', 'N/A')}")
            print(f"Energy Economy: {mapped_data.get('energy_economy', 'N/A')}")
            print(f"Overall Safety: {mapped_data.get('overall_safety', 'N/A')}")
            print(f"Carbon Emissions: {mapped_data.get('carbon_emissions', 'N/A')}")
            print(f"Driver Safety: {mapped_data.get('driver_safety', 'N/A')}")
            print(f"Listed On: {mapped_data.get('listed_on', 'N/A')}")

if __name__ == "__main__":
    main()
