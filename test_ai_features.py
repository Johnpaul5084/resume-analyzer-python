import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/resumes"

def test_rewrite():
    print("\n--- Testing AI Rewrite (Gemini) ---")
    payload = {
        "text": "i worked on python data analysis project using pandas and matplotlib.",
        "section_type": "Experience",
        "target_role": "Data Analyst",
        "company_type": "MNC"
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/rewrite", json=payload)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Success ({duration:.2f}s)")
            print(f"Original: {payload['text']}")
            print(f"Rewritten: {response.json()}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_predict_job():
    print("\n--- Testing Job Prediction (BERT) ---")
    payload = {
        "text": "Experienced software engineer with 5 years in React, Node.js, and AWS. Built scalable microservices.",
        "candidate_labels": ["Frontend Developer", "Backend Developer", "DevOps Engineer", "Data Scientist"]
    }
    
    print("Sending request (first time might be slow as model downloads)...")
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/predict-job", json=payload, timeout=60) # Longer timeout for model download
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Success ({duration:.2f}s)")
            print(f"Prediction: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_validate_fit():
    print("\n--- Testing Role Fit Validation (Gemini) ---")
    payload = {
        "text": "Junior developer with HTML, CSS skills. Learning Python.",
        "target_role": "Senior Data Scientist"
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/validate-fit", json=payload)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Success ({duration:.2f}s)")
            print(f"Validation Result: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rewrite()
    # Uncomment to test prediction (requires model download ~1.5GB)
    # test_predict_job() 
    test_validate_fit()
