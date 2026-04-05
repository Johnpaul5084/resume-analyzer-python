import requests
import json

# Log in
login_url = "http://localhost:8080/api/v1/login/access-token"
login_data = {"username": "test2@example.com", "password": "password"}
r_login = requests.post(login_url, data=login_data)
if r_login.status_code != 200:
    print("Login failed:", r_login.text)
    exit(1)

token = r_login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create dummy PDF
with open("dummy.pdf", "wb") as f:
    f.write(b"%PDF-1.4\n1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n")

# Upload
upload_url = "http://localhost:8080/api/v1/resumes/upload"
files = {"file": ("dummy.pdf", open("dummy.pdf", "rb"), "application/pdf")}
data = {"title": "Test Resume"}

print("Uploading to /upload...")
r_upload = requests.post(upload_url, headers=headers, files=files, data=data)
print(f"Status Code: {r_upload.status_code}")
print(f"Response: {r_upload.text}")
