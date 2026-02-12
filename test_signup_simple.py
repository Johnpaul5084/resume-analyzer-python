import requests
import json
import random

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Generate random email
random_num = random.randint(1000, 9999)
test_email = f"user{random_num}@test.com"

signup_data = {
    "email": test_email,
    "password": "pass123",  # Simple 7-char password
    "full_name": "Test User"
}

print(f"Testing signup with: {test_email}")

try:
    response = requests.post(f"{BASE_URL}/signup", json=signup_data, timeout=10)
    
    with open("signup_test_result.txt", "w") as f:
        f.write(f"Status Code: {response.status_code}\n")
        f.write(f"Response: {response.text}\n")
    
    if response.status_code == 201:
        print("✅ SUCCESS! User created")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ FAILED with status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    with open("signup_test_result.txt", "w") as f:
        f.write(f"Error: {str(e)}\n")
