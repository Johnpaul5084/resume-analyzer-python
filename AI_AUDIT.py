import requests
import time
import sys
import json

BASE_URL = "http://127.0.0.1:8080/api/v1"
TEST_USER = {
    "email": f"audit_{int(time.time())}@resume-analyzer.ai",
    "password": "audit_password_123",
    "full_name": "Audit Bot"
}

token = None

def print_audit(step, status, details=""):
    color = "\033[92m" if "PASS" in status else "\033[91m"
    reset = "\033[0m"
    print(f"{step:<40} {color}{status:<10}{reset} {details}")

def run_audit():
    global token
    print("\n[START] AI Resume Analyzer - Pre-Deployment Intelligence Audit\n" + "="*60)
    
    # 1. Health Check
    try:
        start = time.time()
        res = requests.get("http://127.0.0.1:8080/healthz")
        latency = round(time.time() - start, 3)
        if res.status_code == 200:
            print_audit("System Health", "PASS", f"Latency: {latency}s")
        else:
            print_audit("System Health", "FAIL", f"Status: {res.status_code}")
    except:
        print_audit("System Health", "CRITICAL", "Backend not reachable.")
        return

    # 2. Signup
    start = time.time()
    res = requests.post(f"{BASE_URL}/signup", json=TEST_USER)
    latency = round(time.time() - start, 3)
    if res.status_code == 201:
        print_audit("User Registration", "PASS", f"Latency: {latency}s")
    else:
        print_audit("User Registration", "FAIL", res.text)

    # 3. Login
    start = time.time()
    res = requests.post(f"{BASE_URL}/login/access-token", data={
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    latency = round(time.time() - start, 3)
    if res.status_code == 200:
        token = res.json()["access_token"]
        print_audit("Auth: Login", "PASS", f"Latency: {latency}s")
    else:
        print_audit("Auth: Login", "FAIL", res.text)
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 4. Mentor Chat
    start = time.time()
    res = requests.post(f"{BASE_URL}/ai-mentor/chat", json={
        "question": "What is AI Resume Analyzer?",
        "resume_id": None
    }, headers=headers)
    latency = round(time.time() - start, 3)
    if res.status_code == 200:
        print_audit("Mentor Bot: Chat", "PASS", f"Latency: {latency}s")
    else:
        print_audit("Mentor Bot: Chat", "FAIL", res.text)

    # 5. Mentor Insight (RAG)
    start = time.time()
    res = requests.post(f"{BASE_URL}/ai-mentor/insight", json={
        "resume_text": "Experienced Python Developer with expertise in FastAPI and AI.",
        "skills": ["Python", "FastAPI", "React"]
    }, headers=headers)
    latency = round(time.time() - start, 3)
    if res.status_code == 200:
        print_audit("Mentor Bot: RAG Insight", "PASS", f"Latency: {latency}s")
    else:
        print_audit("Mentor Bot: RAG Insight", "FAIL", res.text)

    # 6. Resume Transform (Advanced Rewriter)
    start = time.time()
    res = requests.post(f"{BASE_URL}/ai-rewrite/transform", json={
        "resume_text": "I build web apps using python.",
        "job_description": "We need an engineer to build high-performance FastAPI applications.",
        "mode": "ATS"
    }, headers=headers)
    latency = round(time.time() - start, 3)
    if res.status_code == 200:
        print_audit("AI Rewriter: JD Transform", "PASS", f"Latency: {latency}s")
    else:
        print_audit("AI Rewriter: JD Transform", "FAIL", res.text)

    # 7. Resume Strategy
    start = time.time()
    res = requests.get(f"{BASE_URL}/ai-mentor/strategy/FAANG", headers=headers)
    latency = round(time.time() - start, 3)
    if res.status_code == 200:
        print_audit("Career Intel: Strategy", "PASS", f"Latency: {latency}s")
    else:
        print_audit("Career Intel: Strategy", "FAIL", res.text)

    print("="*60 + "\n[DONE] Audit Complete.\n")

if __name__ == "__main__":
    run_audit()
