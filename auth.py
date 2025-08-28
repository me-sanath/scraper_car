import requests
import os
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

LOGIN_POST_URL = 'https://november2024version01.dicewebfreelancers.com/index.php/login?task=user.login'

LOGIN_URL = 'https://november2024version01.dicewebfreelancers.com/index.php/login?task=user.login'



def extract_csrf_token(html_content):
    """
    Extract CSRF token from HTML response
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    hidden_inputs = soup.find_all('input', type='hidden')
    for input_field in hidden_inputs:
        if input_field.get('value') and len(input_field.get('value')) == 32:
            return input_field.get('value')
    
    script_pattern = r'"csrf\.token":"([a-f0-9]{32})"'
    script_match = re.search(script_pattern, html_content)
    if script_match:
        return script_match.group(1)
    
    token_pattern = r'([a-f0-9]{32})'
    matches = re.findall(token_pattern, html_content)
    
    for token in matches:
        if html_content.count(token) > 1:
            return token
    
    return None

def main():
    # Create a session to maintain cookies and session state
    session = requests.Session()
    
    # Set headers to mimic a real browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # First request: GET the login page to get CSRF token and establish session
    print("Making GET request to login page...")
    response = session.get(LOGIN_URL)
    
    if response.status_code != 200:
        print(f"Failed to get login page. Status code: {response.status_code}")
        return None, None
    
    print(f"GET request successful. Status code: {response.status_code}")
    print(f"Cookies received: {dict(session.cookies)}")
    
    html_content = response.text
    csrf_token = extract_csrf_token(html_content)
    
    if not csrf_token:
        print("CSRF Token not found")
        return None, None
    
    print(f"CSRF Token extracted: {csrf_token}")

    # Prepare login payload
    payload = {
        'username': 'rajat',  # Hardcoded for testing
        'password': '@Rajatraikar0038',  # Hardcoded for testing
        'return': 'aHR0cHM6Ly9ub3ZlbWJlcjIwMjR2ZXJzaW9uMDEuZGljZXdlYmZyZWVsYW5jZXJzLmNvbS9pbmRleC5waHAvcG9zdC1mcmVlLWFkL3VzZXIvYWRk',
        csrf_token: 1,
    }
    
    print(f"Login payload: {payload}")
    
    # Second request: POST login credentials using the same session
    print("Making POST request to login...")
    response = session.post(LOGIN_POST_URL, data=payload)
    
    print(f"POST request completed. Status code: {response.status_code}")
    print(f"Final cookies: {dict(session.cookies)}")
    print(f"Response URL: {response.url}")
    
    # Save the response
    with open('response.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print("Response saved to response.html")
    
    # Check if login was successful
    if "post-free-ad" in response.url.lower():
        print("Login appears to have succeeded - redirected to post-ad page")
        
        # Verify we can access the post-ad page
        print("Verifying access to post-ad page...")
        post_ad_url = 'https://november2024version01.dicewebfreelancers.com/index.php/post-free-ad/user/add'
        verify_response = session.get(post_ad_url)
        
        if verify_response.status_code == 200:
            # Check if we can see the ad posting form and user is logged in
            if "jomclForm" in verify_response.text and "logout" in verify_response.text.lower():
                print("Successfully accessed post-ad page - user is logged in")
            else:
                print("Access denied to post-ad page - login may have failed")
                return None, None
        else:
            print(f"Failed to access post-ad page: {verify_response.status_code}")
    elif "login" in response.url.lower():
        print("Login appears to have failed - still on login page")
        return None, None
    else:
        print("Login status unclear - check response")
    
    return session, csrf_token

if __name__ == "__main__":
    main()


