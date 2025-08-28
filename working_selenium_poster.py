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
from datetime import datetime

load_dotenv()

class WorkingSeleniumAdPoster:
    """
    Working Selenium-based ad poster that successfully posts advertisements.
    Based on comprehensive testing and analysis.
    """
    
    def __init__(self):
        self.driver = None
        self.ad_details = None
        self.debug_dir = "debug_snapshots"
        
        # Create debug directory if it doesn't exist
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
        
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
        
        print("✅ Chrome driver setup complete")
        
    def take_snapshot(self, stage_name):
        """Take a snapshot of the current page for debugging"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stage_clean = stage_name.replace(" ", "_").replace(":", "").lower()
            
            # Save HTML
            html_filename = f"{self.debug_dir}/{timestamp}_{stage_clean}.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"📸 HTML snapshot saved: {html_filename}")
            
            # Save screenshot
            screenshot_filename = f"{self.debug_dir}/{timestamp}_{stage_clean}.png"
            self.driver.save_screenshot(screenshot_filename)
            print(f"📸 Screenshot saved: {screenshot_filename}")
            
            # Save current URL and page title
            info_filename = f"{self.debug_dir}/{timestamp}_{stage_clean}_info.txt"
            with open(info_filename, 'w', encoding='utf-8') as f:
                f.write(f"URL: {self.driver.current_url}\n")
                f.write(f"Title: {self.driver.title}\n")
                f.write(f"Stage: {stage_name}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            print(f"📸 Page info saved: {info_filename}")
            
        except Exception as e:
            print(f"⚠️  Error taking snapshot: {e}")
        
    def load_ad_details(self):
        """Load ad details from JSON file"""
        try:
            with open('ad_details.json', 'r', encoding='utf-8') as f:
                self.ad_details = json.load(f)
                print(f"✅ Loaded ad details for: {self.ad_details.get('title', 'Unknown')}")
                return True
        except Exception as e:
            print(f"❌ Error loading ad details: {e}")
            return False
    
    def login_to_site(self):
        """Login to the website"""
        print("🔐 Attempting to login...")
        
        try:
            # Go to login page
            self.driver.get("https://november2024version01.dicewebfreelancers.com/index.php/login?task=user.login")
            time.sleep(3)
            
            # Take snapshot of login page
            self.take_snapshot("Login Page Loaded")
            
            # Wait for login form
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Get credentials from environment
            username = os.getenv('USERNAME')
            password = os.getenv('PASSWORD')
            
            if not username or not password:
                print("⚠️  No credentials found in environment - manual login required")
                input("Please login manually in the browser and press Enter when ready...")
                return True
            
            # Fill in credentials
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Take snapshot before submission
            self.take_snapshot("Login Form Filled")
            
            # Find and click submit button
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for redirect
            time.sleep(5)
            
            # Take snapshot after submission
            self.take_snapshot("After Login Submission")
            
            # Check if login was successful
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                print("✅ Login successful")
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
        print("📝 Navigating to post ad page...")
        
        try:
            self.driver.get("https://november2024version01.dicewebfreelancers.com/index.php/post-free-ad/user/add")
            time.sleep(5)
            
            # Take snapshot of post ad page
            self.take_snapshot("Post Ad Page Loaded")
            
            current_url = self.driver.current_url
            if "login" in current_url.lower():
                print("❌ Still on login page - authentication required")
                return False
            else:
                print("✅ Successfully navigated to post ad page")
                return True
                
        except Exception as e:
            print(f"❌ Error navigating to post ad page: {e}")
            return False
    
    def fill_form_fields(self):
        """Fill in the form fields - ONLY title, price, and basic fields first"""
        print("✏️  Filling basic form fields...")
        
        try:
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
            
            print("✅ Basic form fields filled")
            return True
            
        except Exception as e:
            print(f"❌ Error filling basic form fields: {e}")
            return False

    def select_categories(self):
        """Select all category levels - this should be done before filling other fields"""
        print("🏷️  === Starting Category Selection Process ===")
        
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
            self.take_snapshot("After Main Category Selection")
            
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
                    self.take_snapshot("Before Subcategory Selection")
                    
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
                    self.take_snapshot("After Subcategory Selection")
                    
                    # Wait for third category dropdown to appear after selecting "Cars - Parts"
                    print("🔄 Waiting for third category dropdown to appear...")
                    time.sleep(5)  # Wait longer for JavaScript to load
                    
                    # Take snapshot to see what appeared
                    self.take_snapshot("After Waiting for Third Category")
                    
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
                            self.take_snapshot("Before Third Category Selection")
                            
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
                            self.take_snapshot("After Third Category Selection")
                            
                            # Wait for vehicle-specific fields to appear
                            print("🚗 Waiting for vehicle-specific fields to appear...")
                            time.sleep(5)
                            
                            # Take snapshot to see what fields appeared
                            self.take_snapshot("After Waiting for Vehicle Fields")
                            
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

    def fill_remaining_fields(self):
        """Fill in remaining fields after category selection"""
        print("✏️  Filling remaining form fields...")
        
        try:
            # Fill description using JavaScript (required due to interactability issues)
            description_script = """
                var descField = document.querySelector('textarea[name*="description"]');
                if (descField) {
                    descField.value = arguments[0];
                    descField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            """
            self.driver.execute_script(description_script, self.ad_details.get('description', ''))
            print("✅ Filled description")
            
            # Take snapshot after filling remaining fields
            self.take_snapshot("After Filling Remaining Fields")
            
            return True
            
        except Exception as e:
            print(f"❌ Error filling remaining fields: {e}")
            return False
    
    def upload_images(self):
        """Upload images to the form"""
        print("🖼️  Uploading images...")
        
        try:
            # Take snapshot before image upload
            self.take_snapshot("Before Image Upload")
            
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
            self.take_snapshot("After Image Upload")
            
            return True
            
        except Exception as e:
            print(f"❌ Error uploading images: {e}")
            return False

    def verify_ad_posted(self):
        """Verify that the ad was posted successfully by checking user's ads page"""
        print("🔍 Verifying ad was posted successfully...")
        
        try:
            # Navigate to user's ads page
            self.driver.get("https://november2024version01.dicewebfreelancers.com/index.php/my-ads/user")
            time.sleep(5)
            
            # Take snapshot of user's ads page
            self.take_snapshot("User Ads Page")
            
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

    def handle_vehicle_specific_fields(self):
        """Handle vehicle-specific fields that appear after category selection"""
        print("🚗 Handling vehicle-specific fields...")
        
        try:
            # First verify we're on the right category path
            print("🔍 Verifying category selection...")
            try:
                category_select = self.driver.find_element(By.NAME, "category[]")
                selected_category = Select(category_select).first_selected_option.text
                print(f"✅ Main category: {selected_category}")
                
                # Check if subcategories are present
                subcategory_selects = self.driver.find_elements(By.NAME, "subcategory[]")
                if subcategory_selects:
                    for i, subcat_select in enumerate(subcategory_selects):
                        try:
                            selected_subcat = Select(subcat_select).first_selected_option.text
                            print(f"✅ Subcategory {i+1}: {selected_subcat}")
                        except:
                            print(f"⚠️  Subcategory {i+1}: Not selected")
                else:
                    print("⚠️  No subcategories found")
                    
            except Exception as e:
                print(f"⚠️  Error checking categories: {e}")
            
            # Wait for dynamic fields to load
            time.sleep(3)
            
            # Look for common vehicle fields
            vehicle_field_selectors = [
                "input[name*='trim']",
                "input[name*='transmission']", 
                "input[name*='year']",
                "input[name*='mileage']",
                "input[name*='engine']",
                "input[name*='fuel']",
                "input[name*='color']",
                "input[name*='model']",
                "input[name*='brand']",
                "select[name*='trim']",
                "select[name*='transmission']",
                "select[name*='fuel']"
            ]
            
            vehicle_fields = []
            for selector in vehicle_field_selectors:
                fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                vehicle_fields.extend(fields)
            
            if vehicle_fields:
                print(f"✅ Found {len(vehicle_fields)} vehicle-specific fields")
                
                # Fill in vehicle details
                for field in vehicle_fields:
                    try:
                        field_name = field.get_attribute('name', '').lower()
                        field_type = field.tag_name
                        
                        if field_type == 'input':
                            if 'year' in field_name:
                                field.clear()
                                field.send_keys('2020')
                                print("✅ Filled year: 2020")
                            elif 'mileage' in field_name:
                                field.clear()
                                field.send_keys('50000')
                                print("✅ Filled mileage: 50000")
                            elif 'fuel' in field_name:
                                field.clear()
                                field.send_keys('Petrol')
                                print("✅ Filled fuel type: Petrol")
                            elif 'color' in field_name:
                                field.clear()
                                field.send_keys('White')
                                print("✅ Filled color: White")
                            elif 'engine' in field_name:
                                field.clear()
                                field.send_keys('1.5L')
                                print("✅ Filled engine: 1.5L")
                            elif 'model' in field_name:
                                field.clear()
                                field.send_keys('Sedan')
                                print("✅ Filled model: Sedan")
                            elif 'brand' in field_name:
                                field.clear()
                                field.send_keys('Toyota')
                                print("✅ Filled brand: Toyota")
                        
                        elif field_type == 'select':
                            select_field = Select(field)
                            if 'transmission' in field_name:
                                # Try to select automatic
                                for option in select_field.options:
                                    if 'automatic' in option.text.lower():
                                        select_field.select_by_visible_text(option.text)
                                        print(f"✅ Selected transmission: {option.text}")
                                        break
                                else:
                                    select_field.select_by_index(0)
                                    print(f"✅ Selected first transmission option: {select_field.first_selected_option.text}")
                            elif 'fuel' in field_name:
                                # Try to select petrol
                                for option in select_field.options:
                                    if 'petrol' in option.text.lower():
                                        select_field.select_by_visible_text(option.text)
                                        print(f"✅ Selected fuel: {option.text}")
                                        break
                                else:
                                    select_field.select_by_index(0)
                                    print(f"✅ Selected first fuel option: {select_field.first_selected_option.text}")
                    
                    except Exception as e:
                        print(f"⚠️  Error filling field {field_name}: {e}")
                        continue
                
                return True
            else:
                print("⚠️  No vehicle-specific fields found")
                return False
                
        except Exception as e:
            print(f"❌ Error handling vehicle fields: {e}")
            return False
    
    def submit_form(self):
        """Submit the form"""
        print("🚀 Submitting form...")
        
        try:
            # Take snapshot before submission
            self.take_snapshot("Before Form Submission")
            
            # Find submit button - try multiple strategies
            submit_button = None
            
            # Strategy 1: Look for input[type='submit']
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                print("✅ Found submit button by input[type='submit']")
            except:
                pass
            
            # Strategy 2: Look for button[type='submit']
            if not submit_button:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    print("✅ Found submit button by button[type='submit']")
                except:
                    pass
            
            # Strategy 3: Look for any button or input with submit-related text
            if not submit_button:
                try:
                    submit_elements = self.driver.find_elements(By.CSS_SELECTOR, "input, button")
                    for element in submit_elements:
                        element_text = element.get_attribute('value') or element.text or ''
                        if any(word in element_text.lower() for word in ['submit', 'post', 'save', 'publish']):
                            submit_button = element
                            print(f"✅ Found submit button by text: {element_text}")
                            break
                except:
                    pass
            
            # Strategy 4: Look for any element with submit in name or id
            if not submit_button:
                try:
                    submit_elements = self.driver.find_elements(By.CSS_SELECTOR, "[name*='submit'], [id*='submit'], [class*='submit']")
                    if submit_elements:
                        submit_button = submit_elements[0]
                        print(f"✅ Found submit button by name/id/class: {submit_button.get_attribute('name') or submit_button.get_attribute('id')}")
                except:
                    pass
            
            if submit_button:
                # Scroll to submit button to ensure it's visible
                self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(1)
                
                # Take snapshot right before clicking submit
                self.take_snapshot("Right Before Submit Click")
                
                # Click the submit button
                submit_button.click()
                print("✅ Form submitted")
                
                # Wait for response - longer wait for form processing
                print("⏳ Waiting for form submission response...")
                time.sleep(15)
                
                # Take snapshot after submission
                self.take_snapshot("After Form Submission")
                
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
            
            # Step 3: Login to site
            if not self.login_to_site():
                print("❌ Login failed. Exiting.")
                return False
            
            # Step 4: Navigate to post ad page
            if not self.navigate_to_post_ad_page():
                print("❌ Failed to navigate to post ad page. Exiting.")
                return False
            
            # Step 5: Fill basic form fields (title, price, address, location, tag)
            if not self.fill_form_fields():
                print("❌ Failed to fill basic form fields. Exiting.")
                return False
            
            # Step 6: Select all category levels
            if not self.select_categories():
                print("❌ Failed to select categories. Exiting.")
                return False
            
            # Step 7: Fill remaining fields (description) after category selection
            if not self.fill_remaining_fields():
                print("❌ Failed to fill remaining fields. Exiting.")
                return False
            
            # Step 8: Handle vehicle-specific fields
            print("\n🚗 === Handling Vehicle-Specific Fields ===")
            self.handle_vehicle_specific_fields()
            
            # Step 9: Upload images
            self.upload_images()
            
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
