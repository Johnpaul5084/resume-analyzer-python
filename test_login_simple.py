import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Test with the user we just created
login_data = {
    "username": "user9923@test.com",  # FastAPI OAuth2 uses 'username' field
    "password": "pass123"
}

print(f"Testing login with: {login_data['username']}")

try:
    # OAuth2 expects form data, not JSON
    response = requests.post(
        f"{BASE_URL}/login/access-token", 
        data=login_data,  # Use 'data' instead of 'json' for form data
        timeout=10
    )
    
    with open("login_test_result.txt", "w") as f:
        f.write(f"Status Code: {response.status_code}\n")
        f.write(f"Response: {response.text}\n")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Login successful")
        result = response.json()
        print(f"Access Token: {result.get('access_token', 'N/A')[:50]}...")
        print(f"Token Type: {result.get('token_type', 'N/A')}")
    else:
        print(f"❌ FAILED with status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    with open("login_test_result.txt", "w") as f:
        f.write(f"Error: {str(e)}\n")
