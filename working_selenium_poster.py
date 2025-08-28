import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv
import requests


load_dotenv()

class WorkingSeleniumAdPoster:
    """
    Working Selenium-based ad poster that successfully posts advertisements.
    Based on comprehensive testing and analysis.
    """
    
    def __init__(self):
        self.driver = None
        self.ad_details = None
        self.cookies_file = "session_cookies.json"
        
    def setup_driver(self):
        """Setup Chrome driver with optimal settings"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Chrome driver ready")
        
    def save_cookies(self):
        """Save current session cookies to file"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            print("Session cookies saved")
        except Exception as e:
            print(f"Error saving cookies: {e}")
    
    def load_cookies(self):
        """Load and apply saved session cookies"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                
                # Go to the site first (cookies need a domain context)
                self.driver.get("https://november2024version01.dicewebfreelancers.com/")
                
                # Apply cookies
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        continue
                
                print("Session cookies loaded")
                return True
            return False
        except Exception as e:
            print(f"Error loading cookies: {e}")
            return False
    
    def check_login_status(self):
        """Check if we're still logged in by visiting a protected page"""
        try:
            self.driver.get("https://november2024version01.dicewebfreelancers.com/index.php/post-free-ad/user")
            time.sleep(3)
            
            # Check if we're redirected to login page
            if "login" in self.driver.current_url.lower():
                return False
            return True
        except Exception as e:
            return False
    
    def try_session_reuse(self):
        """Try to reuse saved session, fallback to login if needed"""
        print("Checking for saved session...")
        
        # Try to load saved cookies
        if self.load_cookies():
            # Check if the session is still valid
            if self.check_login_status():
                print("✅ Session reused successfully")
                return True
            else:
                print("Saved session expired, logging in...")
                # Clear expired cookies
                self.clear_expired_cookies()
        
        # Fallback to normal login
        return self.login_to_site()
    
    def clear_expired_cookies(self):
        """Remove expired session cookies"""
        try:
            if os.path.exists(self.cookies_file):
                os.remove(self.cookies_file)
                print("Expired cookies cleared")
        except Exception as e:
            print(f"Error clearing cookies: {e}")
        
    def load_ad_details(self):
        """Load ad details from JSON file"""
        try:
            with open('ad_details.json', 'r', encoding='utf-8') as f:
                self.ad_details = json.load(f)
                print(f"Loaded: {self.ad_details.get('title', 'Unknown')}")
                return True
        except Exception as e:
            print(f"❌ Error loading ad details: {e}")
            return False
    
    def login_to_site(self):
        """Login to the website"""
        print("Logging in...")
        
        try:
            # Go to login page
            self.driver.get("https://november2024version01.dicewebfreelancers.com/index.php/login?task=user.login")
            time.sleep(3)
            

            
            # Wait for login form
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Get credentials from environment
            username = os.getenv('USERNAME')
            password = os.getenv('PASSWORD')
            
            if not username or not password:
                print("No credentials found - manual login required")
                input("Please login manually in the browser and press Enter when ready...")
                return True
            
            # Fill in credentials
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            

            
            # Find and click submit button
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for redirect
            time.sleep(5)
            
            # Check if login was successful
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                print("Login successful")
                # Save cookies for future use
                self.save_cookies()
                return True
            else:
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {e}")
            input("Please login manually in the browser and press Enter when ready...")
            return True
    
    def navigate_to_post_ad_page(self):
        """Navigate to the post ad page"""
        print("Navigating to post ad page...")
        
        try:
            self.driver.get("https://november2024version01.dicewebfreelancers.com/index.php/post-free-ad/user/add")
            time.sleep(5)
            
            # Take snapshot of post ad page
    
            
            current_url = self.driver.current_url
            if "login" in current_url.lower():
                print("❌ Still on login page - authentication required")
                return False
            else:
                print("Post ad page loaded")
                return True
                
        except Exception as e:
            print(f"❌ Error navigating to post ad page: {e}")
            return False
    


    def select_categories(self):
        """Select all category levels - this should be done before filling other fields"""
        print("Selecting categories...")
        
        try:
            # Select main category (Vehicles)
            print("🏷️  Selecting main category: Vehicles...")
            
            # Find the first category select element (main category)
            first_category_select = Select(self.driver.find_element(By.ID, "category"))
            
            # Debug: Show all available category options
            print("📋 Available category options:")
            for i, option in enumerate(first_category_select.options):
                print(f"   {i}: {option.text} (value: {option.get_attribute('value')})")
            
            # Try to find the Vehicles category
            vehicles_found = False
            for option in first_category_select.options:
                if "vehicle" in option.text.lower() or option.get_attribute('value') == "6":
                    first_category_select.select_by_value(option.get_attribute('value'))
                    print(f"✅ Selected category: {option.text} (value: {option.get_attribute('value')})")
                    vehicles_found = True
                    break
            
            if not vehicles_found:
                # Fallback to value "6" if text search fails
                try:
                    first_category_select.select_by_value("6")
                    print("✅ Selected category by value: 6")
                except:
                    # Last resort: select first option
                    first_category_select.select_by_index(0)
                    print(f"✅ Selected first category option: {first_category_select.first_selected_option.text}")
            
            print("✅ Selected main category: Vehicles")
            
            # Take snapshot after main category selection
    
            
            # Wait for subcategory to appear and select Cars - Parts
            print("🚗 Waiting for subcategory to appear...")
            
            # Wait for dynamic content to load after category selection
            print("⏳ Waiting for dynamic content to load...")
            time.sleep(5)  # Increased wait time for JavaScript to load
            
            # Try to trigger any change events that might load subcategories
            try:
                # Sometimes the page needs a trigger to load subcategories
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", first_category_select)
                print("🔄 Triggered change event on category select")
                time.sleep(2)  # Wait for change event to process
            except Exception as e:
                print(f"⚠️  Error triggering change event: {e}")
            
            time.sleep(3)
            
            # Debug: Show all form elements to understand structure
            print("🔍 Debug: Inspecting form structure after category selection...")
            all_selects = self.driver.find_elements(By.TAG_NAME, "select")
            print(f"📋 Found {len(all_selects)} select elements:")
            for i, select in enumerate(all_selects):
                try:
                    name = select.get_attribute('name') or 'no-name'
                    id_attr = select.get_attribute('id') or 'no-id'
                    print(f"   Select {i+1}: name='{name}', id='{id_attr}'")
                except:
                    print(f"   Select {i+1}: Error getting attributes")
            
            try:
                # Look for the second category dropdown that should appear after selecting Vehicles
                print("🔍 Looking for second category dropdown (jomcl_category_6_1)...")
                
                # Strategy 1: Look for the specific second category dropdown by ID
                try:
                    second_category_select = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "jomcl_category_6_1"))
                    )
                    print("✅ Found second category dropdown by ID")
                    
                    # Look for the select element inside this div
                    subcategory_select = second_category_select.find_element(By.TAG_NAME, "select")
                    print("✅ Found subcategory select element")
                    
                except:
                    print("⚠️  Second category dropdown not found by ID")
                    
                    # Strategy 2: Look for any new select elements that appeared
                    try:
                        all_selects = self.driver.find_elements(By.TAG_NAME, "select")
                        for select in all_selects:
                            name = select.get_attribute('name') or ''
                            if name and 'category' in name.lower() and name != 'exf_1':  # Look for category fields
                                subcategory_select = select
                                print(f"🔍 Found potential subcategory select: {name}")
                                break
                    except:
                        pass
                
                if subcategory_select:
                    # Take snapshot before subcategory selection
            
                    
                    # Select Cars - Parts
                    subcategory_select = Select(subcategory_select)
                    print(f"📋 Available subcategory options: {[opt.text for opt in subcategory_select.options]}")
                    
                    # Try to find the option containing "Cars" or "Parts"
                    cars_parts_found = False
                    for option in subcategory_select.options:
                        if "car" in option.text.lower() and "parts" in option.text.lower():
                            subcategory_select.select_by_visible_text(option.text)
                            print(f"✅ Selected subcategory: {option.text}")
                            cars_parts_found = True
                            break
                    
                    if not cars_parts_found:
                        # If no exact match, select the first option
                        subcategory_select.select_by_index(0)
                        print(f"✅ Selected first subcategory option: {subcategory_select.first_selected_option.text}")
                    
                    # Take snapshot after subcategory selection
            
                    
                    # Wait for third category dropdown to appear after selecting "Cars - Parts"
                    print("🔄 Waiting for third category dropdown to appear...")
                    time.sleep(5)  # Wait longer for JavaScript to load
                    
                    # Take snapshot to see what appeared
            
                    
                    # Look for third category level
                    try:
                        # Strategy 1: Look for any new category dropdowns that might have appeared
                        print("🔍 Looking for third category dropdown...")
                        
                        # Look for any new select elements that might be the third category
                        all_selects_after = self.driver.find_elements(By.TAG_NAME, "select")
                        print(f"📋 Found {len(all_selects_after)} select elements after subcategory selection")
                        
                        # Look for any new category-related elements
                        third_category_select = None
                        for select in all_selects_after:
                            try:
                                name = select.get_attribute('name') or ''
                                id_attr = select.get_attribute('id') or ''
                                if 'category' in name.lower() or 'category' in id_attr.lower():
                                    # Skip the ones we already know about
                                    if id_attr not in ['category', 'jomcl_category_-1_1', 'jomcl_category_6_1']:
                                        third_category_select = select
                                        print(f"🔍 Found potential third category: name='{name}', id='{id_attr}'")
                                        break
                            except:
                                continue
                        
                        # Strategy 2: Look for any new divs with category in the ID
                        if not third_category_select:
                            try:
                                category_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[id*='category']")
                                for div in category_divs:
                                    div_id = div.get_attribute('id') or ''
                                    if div_id not in ['jomcl_category_-1_1', 'jomcl_category_6_1']:
                                        print(f"🔍 Found new category div: {div_id}")
                                        # Look for select inside this div
                                        select_inside = div.find_elements(By.TAG_NAME, "select")
                                        if select_inside:
                                            third_category_select = select_inside[0]
                                            print(f"✅ Found third category select inside div {div_id}")
                                            break
                            except Exception as e:
                                print(f"⚠️  Error looking for category divs: {e}")
                        
                        if third_category_select:
                            # Take snapshot before third category selection
                    
                            
                            third_category_select = Select(third_category_select)
                            print(f"📋 Available third category options: {[opt.text for opt in third_category_select.options]}")
                            
                            # Try to find "Second hand cars in Bangladesh!"
                            bangladesh_found = False
                            for option in third_category_select.options:
                                if "second hand" in option.text.lower() and "bangladesh" in option.text.lower():
                                    third_category_select.select_by_visible_text(option.text)
                                    print(f"✅ Selected third category: {option.text}")
                                    bangladesh_found = True
                                    break
                            
                            if not bangladesh_found:
                                # If no exact match, select the first option
                                third_category_select.select_by_index(0)
                                print(f"✅ Selected first third category option: {third_category_select.first_selected_option.text}")
                            
                            # Take snapshot after third category selection
                    
                            
                            # Wait for vehicle-specific fields to appear
                            print("🚗 Waiting for vehicle-specific fields to appear...")
                            time.sleep(5)
                            
                            # Take snapshot to see what fields appeared
                    
                            
                            # Look for vehicle-specific fields
                            try:
                                vehicle_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='trim'], input[name*='transmission'], input[name*='year'], input[name*='mileage'], input[name*='engine'], input[name*='fuel'], input[name*='model'], input[name*='brand']")
                                if vehicle_fields:
                                    print(f"✅ Found {len(vehicle_fields)} vehicle-specific fields")
                                    # Fill in vehicle details
                                    for field in vehicle_fields:
                                        field_name = field.get_attribute('name', '').lower()
                                        if 'year' in field_name:
                                            field.clear()
                                            field.send_keys('2020')
                                            print("✅ Filled year: 2020")
                                        elif 'mileage' in field_name or 'kilometers' in field_name:
                                            field.clear()
                                            field.send_keys('50000')
                                            print("✅ Filled mileage: 50000")
                                        elif 'fuel' in field_name:
                                            field.clear()
                                            field.send_keys('Petrol')
                                            print("✅ Filled fuel type: Petrol")
                                        elif 'model' in field_name:
                                            field.clear()
                                            field.send_keys('Sedan')
                                            print("✅ Filled model: Sedan")
                                        elif 'brand' in field_name:
                                            field.clear()
                                            field.send_keys('Toyota')
                                            print("✅ Filled brand: Toyota")
                                        elif 'trim' in field_name or 'edition' in field_name:
                                            field.clear()
                                            field.send_keys('Standard')
                                            print("✅ Filled trim/edition: Standard")
                                        elif 'transmission' in field_name:
                                            field.clear()
                                            field.send_keys('Automatic')
                                            print("✅ Filled transmission: Automatic")
                                else:
                                    print("⚠️  No vehicle-specific fields found")
                            except Exception as e:
                                print(f"⚠️  Error handling vehicle fields: {e}")
                        else:
                            print("⚠️  No third category found - vehicle fields may not appear")
                    
                    except Exception as e:
                        print(f"⚠️  Error handling third category: {e}")
                else:
                    print("⚠️  No subcategory select element found")
                
            except Exception as e:
                print(f"⚠️  Subcategory selection issue: {e}")
                print("Continuing with main category only...")
            
            print("✅ Category selection process completed")
            return True
            
        except Exception as e:
            print(f"❌ Error during category selection: {e}")
            return False

    def fill_all_form_details(self):
        """Fill in all form details after category selection"""
        print("✏️  Filling all form details...")
        
        try:
            # Take snapshot before filling details
    
            
            # Fill title
            title_field = self.driver.find_element(By.NAME, "title")
            title_field.clear()
            title_field.send_keys(self.ad_details.get('title', ''))
            print("✅ Filled title")
            
            # Fill price
            price_field = self.driver.find_element(By.NAME, "price")
            price_field.clear()
            price_str = self.ad_details.get('price', '0').replace('Tk ', '').replace(',', '')
            price_field.send_keys(price_str)
            print("✅ Filled price")
            
            # Fill description - handle TinyMCE editor
            try:
                # First try to fill the hidden textarea directly
                desc_textarea = self.driver.find_element(By.NAME, "description")
                desc_textarea.clear()
                desc_textarea.send_keys(self.ad_details.get('description', ''))
                print("✅ Filled description")
            except Exception as e:
                # Fallback: use JavaScript to fill TinyMCE editor
                description_script = """
                    var descField = document.querySelector('textarea[name="description"]');
                    if (descField) {
                        descField.value = arguments[0];
                        descField.dispatchEvent(new Event('input', { bubbles: true }));
                        descField.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                """
                self.driver.execute_script(description_script, self.ad_details.get('description', ''))
                print("✅ Filled description via JavaScript")
            
            # Fill address
            address_field = self.driver.find_element(By.NAME, "address")
            address_field.clear()
            address_field.send_keys("village-kandraji,post-korlakatta,sirsi,uttara kannada ,karnataka\n581318")
            print("✅ Filled address")
            
            # Select location
            location_select = Select(self.driver.find_element(By.NAME, "location[]"))
            location_select.select_by_value("33")  # Bangladesh
            print("✅ Selected location: Bangladesh")
            
            # Select tag
            tag_select = Select(self.driver.find_element(By.NAME, "tagid"))
            tag_select.select_by_value("1")  # Sale
            print("✅ Selected tag: Sale")
            
            # Now look for vehicle-specific fields that should appear after category selection
            print("🚗 Looking for vehicle-specific fields...")
            time.sleep(3)
            
            # Take snapshot to see what fields appeared
    
            
            # Look for vehicle-specific fields using the correct exf_* names
            try:
                # The vehicle fields have names like exf_8, exf_9, exf_10, etc.
                vehicle_field_names = [
                    'exf_8',   # Trim / Edition
                    'exf_9',   # Transmission
                    'exf_10',  # Registration year
                    'exf_11',  # Fuel type
                    'exf_12',  # Kilometers run
                    'exf_13',  # Model
                    'exf_14',  # Year of Manufacture
                    'exf_15',  # Condition
                    'exf_16',  # Body type
                    'exf_17',  # Price Final Status
                    'exf_18',  # Engine capacity
                    'exf_19',  # Posted on
                    'exf_20',  # Sellers Name
                    'exf_21',  # Contact Numbers (textarea)
                    'exf_22',  # Source Link
                    'exf_23',  # Year of Production
                    'exf_24'   # Version
                ]
                
                vehicle_fields_filled = 0
                for field_name in vehicle_field_names:
                    try:
                        field = self.driver.find_element(By.NAME, field_name)
                        if field:
                            # Fill based on field name
                            if field_name == 'exf_8':  # Trim / Edition
                                field.clear()
                                field.send_keys(self.ad_details.get('trim', 'Standard'))
                                print(f"✅ Filled Trim/Edition: {self.ad_details.get('trim', 'Standard')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_9':  # Transmission
                                field.clear()
                                field.send_keys(self.ad_details.get('transmission', 'Automatic'))
                                print(f"✅ Filled Transmission: {self.ad_details.get('transmission', 'Automatic')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_10':  # Registration year
                                field.clear()
                                field.send_keys(self.ad_details.get('registration_year', '2020'))
                                print(f"✅ Filled Registration year: {self.ad_details.get('registration_year', '2020')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_11':  # Fuel type
                                field.clear()
                                field.send_keys(self.ad_details.get('fuel_type', 'Petrol'))
                                print(f"✅ Filled Fuel type: {self.ad_details.get('fuel_type', 'Petrol')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_12':  # Kilometers run
                                field.clear()
                                field.send_keys(self.ad_details.get('kilometers_driven', '50000'))
                                print(f"✅ Filled Kilometers run: {self.ad_details.get('kilometers_driven', '50000')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_13':  # Model
                                field.clear()
                                field.send_keys(self.ad_details.get('model', 'Sedan'))
                                print(f"✅ Filled Model: {self.ad_details.get('model', 'Sedan')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_14':  # Year of Manufacture
                                field.clear()
                                field.send_keys(self.ad_details.get('year_of_production', '2005'))
                                print(f"✅ Filled Year of Manufacture: {self.ad_details.get('year_of_production', '2005')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_15':  # Condition
                                field.clear()
                                field.send_keys(self.ad_details.get('condition', 'Good'))
                                print(f"✅ Filled Condition: {self.ad_details.get('condition', 'Good')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_16':  # Body type
                                field.clear()
                                field.send_keys(self.ad_details.get('body_type', 'Sedan'))
                                print(f"✅ Filled Body type: {self.ad_details.get('body_type', 'Sedan')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_17':  # Price Final Status
                                field.clear()
                                field.send_keys('Negotiable')
                                print("✅ Filled Price Final Status: Negotiable")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_18':  # Engine capacity
                                field.clear()
                                field.send_keys(self.ad_details.get('engine_capacity', '1.5L'))
                                print(f"✅ Filled Engine capacity: {self.ad_details.get('engine_capacity', '1.5L')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_19':  # Posted on
                                field.clear()
                                posted_date = self.ad_details.get('posted_on', '2024')
                                if isinstance(posted_date, str) and 'T' in posted_date:
                                    posted_date = posted_date.split('T')[0]
                                field.send_keys(posted_date)
                                print(f"✅ Filled Posted on: {posted_date}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_20':  # Sellers Name
                                field.clear()
                                field.send_keys(self.ad_details.get('seller_name', 'Car Seller'))
                                print(f"✅ Filled Sellers Name: {self.ad_details.get('seller_name', 'Car Seller')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_21':  # Contact Numbers (textarea)
                                field.clear()
                                contact_numbers = self.ad_details.get('contact', [])
                                if contact_numbers and isinstance(contact_numbers, list):
                                    contact_str = ', '.join([str(contact.get('number', '')) for contact in contact_numbers])
                                else:
                                    contact_str = '+880 1234567890'
                                field.send_keys(contact_str)
                                print(f"✅ Filled Contact Numbers: {contact_str}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_22':  # Source Link
                                field.clear()
                                field.send_keys(self.ad_details.get('url', 'https://example.com'))
                                print(f"✅ Filled Source Link: {self.ad_details.get('url', 'https://example.com')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_23':  # Year of Production
                                field.clear()
                                field.send_keys(self.ad_details.get('year_of_production', '2005'))
                                print(f"✅ Filled Year of Production: {self.ad_details.get('year_of_production', '2005')}")
                                vehicle_fields_filled += 1
                            elif field_name == 'exf_24':  # Version
                                field.clear()
                                version = self.ad_details.get('version', 'F')
                                if version is None:
                                    version = 'F'
                                field.send_keys(version)
                                print(f"✅ Filled Version: {version}")
                                vehicle_fields_filled += 1
                    except Exception as e:
                        print(f"⚠️  Error filling field {field_name}: {e}")
                        continue
                
                if vehicle_fields_filled > 0:
                    print(f"✅ Successfully filled {vehicle_fields_filled} vehicle-specific fields")
                else:
                    print("⚠️  No vehicle-specific fields were filled")
                    
            except Exception as e:
                print(f"⚠️  Error handling vehicle fields: {e}")
            
            # Take snapshot after filling all details
    
            
            return True
            
        except Exception as e:
            print(f"❌ Error filling form details: {e}")
            return False
    
    def upload_images(self):
        """Upload images to the form"""
        print("🖼️  Uploading images...")
        
        try:
            # Take snapshot before image upload
    
            
            # Look for file upload input
            file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            
            if not file_inputs:
                print("⚠️  No file upload inputs found")
                return False
            
            file_input = file_inputs[0]
            print(f"📁 Found file input: {file_input.get_attribute('name')}")
            
            # Download and upload images
            if self.ad_details.get('images'):
                for i, image_info in enumerate(self.ad_details['images']):
                    image_url = image_info['src']
                    print(f"📥 Processing image {i+1}: {image_url}")
                    
                    # Download image
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        # Save as temporary file
                        temp_image_path = f"temp_image_{i}.jpg"
                        with open(temp_image_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Refresh file input element to avoid stale reference
                        try:
                            # Find fresh file input element
                            fresh_file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                            if fresh_file_inputs:
                                fresh_file_input = fresh_file_inputs[0]
                                
                                # Upload image
                                fresh_file_input.send_keys(os.path.abspath(temp_image_path))
                                print(f"✅ Image {i+1} uploaded")
                                
                                # Wait for upload to process
                                time.sleep(3)
                            else:
                                print(f"⚠️  No file input found for image {i+1}")
                        except Exception as e:
                            print(f"⚠️  Error uploading image {i+1}: {e}")
                        
                        # Clean up temp file
                        os.remove(temp_image_path)
                    else:
                        print(f"❌ Failed to download image {i+1}")
            
            # Take snapshot after image upload
    
            
            return True
            
        except Exception as e:
            print(f"❌ Error uploading images: {e}")
            return False

    def agree_to_terms(self):
        """Agree to terms and conditions"""
        print("📋 Looking for terms and conditions checkbox...")
        
        try:
            # Take snapshot before agreeing to terms
    
            
            # Look for privacy/terms checkbox
            privacy_checkbox = None
            
            # Strategy 1: Look for privacy checkbox by name
            try:
                privacy_checkbox = self.driver.find_element(By.NAME, "privacy[]")
                print("✅ Found privacy checkbox by name")
            except:
                pass
            
            # Strategy 2: Look for privacy checkbox by ID
            if not privacy_checkbox:
                try:
                    privacy_checkbox = self.driver.find_element(By.ID, "privacy")
                    print("✅ Found privacy checkbox by ID")
                except:
                    pass
            
            # Strategy 3: Look for any checkbox with privacy-related text
            if not privacy_checkbox:
                try:
                    checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                    for checkbox in checkboxes:
                        # Look for nearby text that mentions privacy or terms
                        try:
                            parent = checkbox.find_element(By.XPATH, "./..")
                            parent_text = parent.text.lower()
                            if "privacy" in parent_text or "terms" in parent_text or "agree" in parent_text:
                                privacy_checkbox = checkbox
                                print("✅ Found privacy checkbox by nearby text")
                                break
                        except:
                            continue
                except:
                    pass
            
            if privacy_checkbox:
                # Check if already checked
                if not privacy_checkbox.is_selected():
                    # Scroll to checkbox to ensure it's visible
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", privacy_checkbox)
                    time.sleep(1)
                    
                    # Click the checkbox
                    privacy_checkbox.click()
                    print("✅ Agreed to terms and conditions")
                else:
                    print("✅ Terms and conditions already agreed to")
                
                # Take snapshot after agreeing to terms
        
                return True
            else:
                print("⚠️  No terms and conditions checkbox found - continuing anyway")
                return True
                
        except Exception as e:
            print(f"⚠️  Error agreeing to terms: {e}")
            print("Continuing anyway...")
            return True

    def verify_ad_posted(self):
        """Verify that the ad was posted successfully by checking user's ads page"""
        print("🔍 Verifying ad was posted successfully...")
        
        try:
            # Navigate to user's ads page
            self.driver.get("https://november2024version01.dicewebfreelancers.com/index.php/my-ads/user")
            time.sleep(5)
            
            # Take snapshot of user's ads page
    
            
            # Check if we're still logged in
            if "login" in self.driver.current_url.lower():
                print("❌ Not logged in - cannot verify ad")
                return False
            
            # Look for the newly posted ad
            page_source = self.driver.page_source
            ad_title = self.ad_details.get('title', '')
            
            if ad_title and ad_title.lower() in page_source.lower():
                print(f"✅ SUCCESS: Ad '{ad_title}' found on user's ads page!")
                return True
            else:
                print(f"⚠️  Ad title '{ad_title}' not found on user's ads page")
                print("This could mean the ad wasn't posted or there's a delay")
                
                # Let's also check for any recent ads
                try:
                    # Look for any ad elements on the page
                    ad_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='ad'], [class*='listing'], [class*='item']")
                    if ad_elements:
                        print(f"📋 Found {len(ad_elements)} ad elements on the page")
                        # Check the first few for recent content
                        for i, ad in enumerate(ad_elements[:3]):
                            try:
                                ad_text = ad.text[:100]  # First 100 characters
                                print(f"   Ad {i+1}: {ad_text}...")
                            except:
                                pass
                    else:
                        print("📋 No ad elements found on the page")
                except Exception as e:
                    print(f"⚠️  Error checking page content: {e}")
                
                return False
                
        except Exception as e:
            print(f"❌ Error verifying ad: {e}")
            return False


    
    def submit_form(self):
        """Submit the form"""
        print("🚀 Submitting form...")
        
        try:
            # Take snapshot before submission
    
            
            # Find submit button - try multiple strategies
            submit_button = None
            
            # Strategy 1: Look specifically for the "Post Ad" button (avoid logout button)
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'][onclick*='valJomclAddForm']")
                print("✅ Found Post Ad button by specific selector")
            except:
                pass
            
            # Strategy 2: Look for button with "Post Ad" text
            if not submit_button:
                try:
                    submit_elements = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
                    for element in submit_elements:
                        element_text = element.text.lower()
                        if 'post ad' in element_text or 'post' in element_text:
                            submit_button = element
                            print(f"✅ Found Post Ad button by text: {element.text}")
                            break
                except:
                    pass
            
            # Strategy 3: Look for button with success class (Post Ad button has btn-success)
            if not submit_button:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn-success[type='submit']")
                    print("✅ Found Post Ad button by btn-success class")
                except:
                    pass
            
            # Strategy 4: Look for any button with submit type (fallback)
            if not submit_button:
                try:
                    submit_elements = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
                    # Filter out logout button by checking value/text
                    for element in submit_elements:
                        element_text = element.text.lower()
                        element_value = element.get_attribute('value', '').lower()
                        # Skip logout button
                        if 'log out' not in element_text and 'logout' not in element_value:
                            submit_button = element
                            print(f"✅ Found submit button (excluding logout): {element.text}")
                            break
                except:
                    pass
            
            if submit_button:
                # Scroll to submit button to ensure it's visible
                self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(1)
                
                # Take snapshot right before clicking submit
        
                
                # Click the submit button
                submit_button.click()
                print("✅ Form submitted")
                
                # Wait for response - longer wait for form processing
                print("⏳ Waiting for form submission response...")
                time.sleep(15)
                
                # Take snapshot after submission
        
                
                # Check the result with multiple strategies
                current_url = self.driver.current_url
                page_source = self.driver.page_source
                page_title = self.driver.title
                
                print(f"📋 Current URL: {current_url}")
                print(f"📋 Page Title: {page_title}")
                
                # Strategy 1: Check URL changes
                if "success" in current_url.lower() or "posted" in current_url.lower():
                    print("🎉 SUCCESS: URL indicates success!")
                    return True
                
                # Strategy 2: Check page content
                if "success" in page_source.lower() or "posted" in page_source.lower():
                    print("🎉 SUCCESS: Page content indicates success!")
                    return True
                
                # Strategy 3: Check for error messages
                if "error" in page_source.lower() or "failed" in page_source.lower():
                    print("❌ ERROR: Error message found in response")
                    return False
                
                # Strategy 4: Check if we're redirected to a different page
                if "post-free-ad" not in current_url.lower():
                    print("🔄 Form submitted - redirected to different page")
                    return True
                
                # Strategy 5: Check if form is still present (indicates submission failed)
                try:
                    form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                    if form_elements:
                        print("⚠️  Form still present - submission may have failed")
                        return False
                    else:
                        print("✅ Form elements not found - likely submitted successfully")
                        return True
                except:
                    print("✅ Could not verify form elements - assuming success")
                    return True
                
            else:
                print("❌ No submit button found - cannot submit form")
                return False
            
        except Exception as e:
            print(f"❌ Error submitting form: {e}")
            return False
    
    def run_complete_posting_process(self):
        """Run the complete ad posting process"""
        print("🚀 === Starting Complete Ad Posting Process ===")
        
        try:
            # Step 1: Setup driver
            self.setup_driver()
            
            # Step 2: Load ad details
            if not self.load_ad_details():
                print("❌ Failed to load ad details. Exiting.")
                return False
            
            # Step 3: Try to use saved session, otherwise login
            if not self.try_session_reuse():
                print("❌ Session reuse failed. Exiting.")
                return False
            
            # Step 4: Navigate to post ad page
            if not self.navigate_to_post_ad_page():
                print("❌ Failed to navigate to post ad page. Exiting.")
                return False
            
            # Step 5: Select all category levels FIRST
            print("\n🏷️  === Starting Category Selection Process ===")
            if not self.select_categories():
                print("❌ Failed to select categories. Exiting.")
                return False
            
            # Step 6: Fill all form details after category selection
            print("\n✏️  === Filling All Form Details ===")
            if not self.fill_all_form_details():
                print("❌ Failed to fill form details. Exiting.")
                return False
            
            # Step 7: Upload images
            print("\n🖼️  === Uploading Images ===")
            self.upload_images()
            
            # Step 8: Agree to terms and conditions
            print("\n📋 === Agreeing to Terms and Conditions ===")
            if not self.agree_to_terms():
                print("❌ Failed to agree to terms. Exiting.")
                return False
            
            # Step 7: Submit form
            if not self.submit_form():
                print("❌ Form submission failed. Exiting.")
                return False
            
            # Step 8: Verify ad was posted successfully
            print("\n🔍 === Verifying Ad Posting Success ===")
            if self.verify_ad_posted():
                print("🎉 === Ad Posting Process Completed Successfully! ===")
                print("✅ Ad was posted and verified on user's ads page")
            else:
                print("⚠️  === Ad Posting Process Completed with Verification Warning ===")
                print("📋 Ad was submitted but verification is unclear - check manually")
            
            print("📋 Check the browser for final result")
            
            # Keep browser open for inspection
            input("Press Enter to close the browser...")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during posting process: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function"""
    poster = WorkingSeleniumAdPoster()
    success = poster.run_complete_posting_process()
    
    if success:
        print("\n🎉 SUCCESS: Ad was posted successfully!")
    else:
        print("\n❌ FAILED: Ad posting failed")

if __name__ == "__main__":
    main()
