import requests
import json
import os
from auth import main as authenticate
from bs4 import BeautifulSoup
import time

# URLs
BASE_URL = "https://november2024version01.dicewebfreelancers.com"
UPLOAD_URL = "https://november2024version01.dicewebfreelancers.com/index.php?option=com_jomclassifieds&task=upload&format=raw&id={ad_id}"
AD_URL = "https://november2024version01.dicewebfreelancers.com/index.php/post-free-ad/user/save"

def load_ad_details():
    """Load ad details from JSON file"""
    try:
        with open('ad_details.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ ad_details.json not found")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON in ad_details.json")
        return None

def upload_image_fixed(session, image_path, ad_id, csrf_token=None):
    """Upload image using the correct endpoint and field name"""
    try:
        # Check if image file exists
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return None
        
        # Construct the upload URL with the ad_id
        upload_url = UPLOAD_URL.format(ad_id=ad_id)
        
        # Prepare upload data
        files = {
            'images': ('image.jpg', open(image_path, 'rb'), 'image/jpeg')
        }
        
        data = {
            'id': str(ad_id)
        }
        
        # Add CSRF token if provided
        if csrf_token:
            data['csrf_token'] = csrf_token
            print(f"🔒 CSRF token added to upload: {csrf_token[:20]}...")
        
        print(f"📤 Uploading image: {image_path}")
        print(f"🔗 Upload URL: {upload_url}")
        print(f"🆔 Ad ID: {ad_id}")
        
        response = session.post(upload_url, files=files, data=data)
        
        print(f"📊 Upload Response Status: {response.status_code}")
        print(f"📄 Upload Response Content: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                # Try to parse JSON response
                result = response.json()
                if 'success' in result and result['success']:
                    print(f"✅ Image uploaded successfully: {result}")
                    return result.get('data', {}).get('path', image_path)
                else:
                    print(f"❌ Upload failed: {result}")
                    return None
            except json.JSONDecodeError:
                # If not JSON, check if it's HTML (login page)
                if '<html' in response.text.lower():
                    print("❌ Got HTML response - likely need to login again")
                    return None
                else:
                    print(f"✅ Image uploaded (non-JSON response): {response.text[:100]}")
                    return image_path
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading image: {e}")
        return None

def construct_form_data(ad_details, ad_id, image_paths=None, csrf_token=None):
    """Construct form data for posting ad based on actual network recording"""
    # Map ad_details to the actual form field names from the HAR file
    form_data = {
        'title': ad_details.get('title', 'Car for Sale'),
        'category[]': ['6', '8', '31'],  # Based on HAR file - these are the actual category IDs
        'exf_8': ad_details.get('trim', 'F'),  # Trim/Version
        'exf_9': ad_details.get('transmission', 'Automatic'),  # Transmission
        'exf_10': ad_details.get('registration_year', '2009'),  # Registration year
        'exf_11': ad_details.get('fuel_type', 'Octane'),  # Fuel type
        'exf_12': ad_details.get('kilometers_driven', '154,000 km'),  # Mileage
        'exf_13': ad_details.get('model', 'Car'),  # Model
        'exf_14': ad_details.get('year_of_production', '2005'),  # Year of production
        'exf_15': ad_details.get('condition', 'Used'),  # Condition
        'exf_16': ad_details.get('body_type', 'Saloon'),  # Body type
        'exf_17': ad_details.get('price', 'Tk 1,550,000'),  # Price
        'exf_18': ad_details.get('engine_capacity', '1,500 cc'),  # Engine capacity
        'exf_19': ad_details.get('posted_on', '2025-08-28T01:44:35+06:00'),  # Posted date
        'exf_20': ad_details.get('seller_name', 'Seller'),  # Seller name
        'exf_21': json.dumps(ad_details.get('contact', [])),  # Contact info as JSON
        'exf_22': ad_details.get('url', ''),  # Source URL
        'exf_23': ad_details.get('year_of_production', '2005'),  # Year again
        'exf_24': ad_details.get('version', 'null'),  # Version
        'price': ad_details.get('price', 'Tk 1,550,000'),  # Price field
        'currency': 'TK',  # Currency
        'tagid': '1',  # Tag ID
        'description': f"<div><div>{ad_details.get('description', 'Good condition car for sale')}</div></div>",  # Description
        'address': 'village-kandraji,post-korlakatta,sirsi,uttara kannada ,karnataka\n581318',  # Address
        'location[]': '33',  # Location ID
        'topaddays': '',  # Top ad days
        'privacy[]': 'on',  # Privacy
        'mode': 'new',  # Mode
        'extImages': '',  # External images
        'userid': '4340',  # User ID (hardcoded from HAR)
        'id': str(ad_id),  # Ad ID
        'latitude': '',  # Latitude
        'langtitude': '',  # Longitude
        'defLocation': 'village-kandraji,post-korlakatta,sirsi,uttara kannada ,karnataka\n581318'  # Default location
    }
    
    # Add images if provided
    if image_paths:
        form_data['images[]'] = image_paths
    
    # Add CSRF token - this is the key part that was wrong
    if csrf_token:
        # The CSRF token field name is the token itself, not 'csrf_token'
        form_data[csrf_token] = '1'
        print(f"🔒 CSRF token added: {csrf_token[:20]}...")
    else:
        print("⚠️  No CSRF token provided")
    
    return form_data

def post_ad(session, form_data):
    """Post the ad using the form data"""
    try:
        print(f"📝 Posting ad with ID: {form_data['id']}")
        print(f"🔗 Post URL: {AD_URL}")
        
        # Use multipart/form-data as shown in the HAR file
        response = session.post(AD_URL, data=form_data)
        
        print(f"📊 Post Response Status: {response.status_code}")
        print(f"📄 Post Response Content: {response.text[:500]}...")
        
        # Save response for debugging
        with open('post_ad_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        if response.status_code == 200 or response.status_code == 303:
            if 'success' in response.text.lower() or 'posted' in response.text.lower() or 'saved' in response.text.lower():
                print("✅ Ad posted successfully!")
                return True
            elif response.status_code == 303:
                # 303 redirect usually means success
                print("✅ Ad posted successfully! (303 redirect)")
                return True
            else:
                print("❌ Ad posting failed - check response content")
                return False
        else:
            print(f"❌ Ad posting failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error posting ad: {e}")
        return False

def main():
    """Main function to post ad with images"""
    print("🚗 Starting Ad Posting Process")
    print("=" * 50)
    
    # Load ad details
    ad_details = load_ad_details()
    if not ad_details:
        return
    
    print(f"📋 Loaded ad details: {ad_details.get('title', 'Unknown')}")
    
    # Authenticate
    print("\n🔐 Authenticating...")
    session, csrf_token = authenticate()
    
    if not session:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Set ad ID for this session
    ad_id = '678948'  # Use consistent ID for both upload and form
    
    # Upload images
    print(f"\n🖼️  Uploading {len(ad_details.get('images', []))} images...")
    uploaded_image_paths = []
    
    for i, img in enumerate(ad_details.get('images', [])):
        if isinstance(img, dict) and 'src' in img:
            image_url = img['src']
            # Download image to local file
            try:
                img_response = session.get(image_url)
                if img_response.status_code == 200:
                    local_path = f"temp_image_{i}.jpg"
                    with open(local_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    # Upload the local image
                    uploaded_path = upload_image_fixed(session, local_path, ad_id, csrf_token)
                    if uploaded_path:
                        uploaded_image_paths.append(uploaded_path)
                        print(f"✅ Image {i+1} uploaded: {uploaded_path}")
                    else:
                        print(f"❌ Failed to upload image {i+1}")
                    
                    # Clean up local file
                    os.remove(local_path)
                else:
                    print(f"❌ Failed to download image {i+1}: {img_response.status_code}")
            except Exception as e:
                print(f"❌ Error processing image {i+1}: {e}")
    
    print(f"\n📊 Total images uploaded: {len(uploaded_image_paths)}")
    
    # Refresh CSRF token before posting (tokens can expire)
    print("\n🔄 Refreshing CSRF token...")
    try:
        # Get the post-ad page to get a fresh CSRF token
        post_ad_page_url = 'https://november2024version01.dicewebfreelancers.com/index.php/post-free-ad/user/add'
        refresh_response = session.get(post_ad_page_url)
        if refresh_response.status_code == 200:
            # Extract fresh CSRF token from the JSON script tag
            import re
            csrf_pattern = r'"csrf\.token":"([a-f0-9]{32})"'
            csrf_match = re.search(csrf_pattern, refresh_response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF token refreshed: {csrf_token[:20]}...")
            else:
                print("⚠️  Could not refresh CSRF token, using original")
        else:
            print("⚠️  Could not refresh CSRF token, using original")
    except Exception as e:
        print(f"⚠️  Error refreshing CSRF token: {e}, using original")
    
    # Construct form data
    print("\n📝 Constructing form data...")
    form_data = construct_form_data(ad_details, ad_id, uploaded_image_paths, csrf_token)
    
    # Post the ad
    print("\n🚀 Posting ad...")
    success = post_ad(session, form_data)
    
    if success:
        print("\n🎉 SUCCESS: Ad posted successfully!")
    else:
        print("\n❌ FAILED: Ad posting failed")
    
    print("\n" + "=" * 50)
    print("🏁 Process completed")

if __name__ == "__main__":
    main()
