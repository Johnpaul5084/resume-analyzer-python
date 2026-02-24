import requests
import time

BASE_URL = "http://127.0.0.1:8080/api/v1"
TEST_USER = {
    "email": f"test_{int(time.time())}@test.com",
    "password": "password123",
    "full_name": "Test User"
}

def test_ai():
    # 1. Signup
    requests.post(f"{BASE_URL}/signup", json=TEST_USER)
    
    # 2. Login
    res = requests.post(f"{BASE_URL}/login/access-token", data={
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Chat
    res = requests.post(f"{BASE_URL}/ai-mentor/chat", json={
        "question": "What is AI Resume Analyzer?",
        "resume_id": None
    }, headers=headers)
    print(f"Chat Response: {res.json()}")

    # 4. Transform
    res = requests.post(f"{BASE_URL}/ai-rewrite/transform", json={
        "resume_text": "I build web apps using python.",
        "job_description": "We need an engineer to build high-performance FastAPI applications.",
        "mode": "ATS"
    }, headers=headers)
    print(f"Transform Response: {res.json()[:100]}...")

if __name__ == "__main__":
    test_ai()
