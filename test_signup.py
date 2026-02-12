import requests
import json
import random

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Generate random email to avoid conflicts
random_num = random.randint(1000, 9999)
test_email = f"testuser{random_num}@example.com"

print("Testing Signup Endpoint")
print("=" * 50)

# Test signup
signup_data = {
    "email": test_email,
    "password": "testpass123",
    "full_name": "Test User"
}

print(f"\n1. Creating user: {test_email}")
print(f"   Request: POST {BASE_URL}/signup")
print(f"   Data: {json.dumps(signup_data, indent=2)}")

try:
    response = requests.post(f"{BASE_URL}/signup", json=signup_data)
    print(f"\n   Response Status: {response.status_code}")
    print(f"   Response Headers: {dict(response.headers)}")
    
    if response.status_code == 201:
        print("   ✅ SUCCESS! User created")
        user_data = response.json()
        print(f"   User Data: {json.dumps(user_data, indent=2)}")
    else:
        print(f"   ❌ FAILED")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ CONNECTION ERROR: Cannot connect to backend")
    print(f"   Make sure backend is running on port 8000")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 50)
