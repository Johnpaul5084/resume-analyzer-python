import google.generativeai as genai
import os
import sys

# Add parent directory to path to import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resume-analyzer-backend'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv('resume-analyzer-backend/.env')

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file")
    print("Please add your Gemini API key to resume-analyzer-backend/.env")
    exit(1)

print(f"[OK] API Key found: {api_key[:10]}...{api_key[-5:]}")
print("\n[TEST] Testing Gemini API with gemini-1.5-flash model...\n")

try:
    genai.configure(api_key=api_key)
    
    # Test with the NEW model name
    print("[INFO] Creating model: gemini-1.5-flash")
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    print("[UP] Sending test prompt...")
    response = model.generate_content("Rewrite this professionally: I did data analysis using Python")
    
    print("\n[SUCCESS] Gemini API is working!\n")
    print("RES:")
    print("-" * 50)
    print(response.text)
    print("-" * 50)
    print("\n[DONE] The AI rewrite feature should work in your application!")
    
except Exception as e:
    print(f"\n[ERROR] {str(e)}\n")
    
    if "404" in str(e) and "gemini-pro" in str(e):
        print("⚠️  The error mentions 'gemini-pro' which means:")
        print("   - The code might not be using the updated model name")
        print("   - OR there's a caching issue")
        print("\n🔧 Try:")
        print("   1. Restart the backend server")
        print("   2. Clear Python cache: rm -rf __pycache__ app/__pycache__")
        print("   3. Run this test again")
    elif "404" in str(e):
        print("⚠️  Model not found. This could mean:")
        print("   - Invalid API key")
        print("   - API key doesn't have access to Gemini 1.5")
        print("   - Network/firewall issue")
        print("\n🔧 Try:")
        print("   1. Verify your API key at https://makersuite.google.com/app/apikey")
        print("   2. Create a new API key if needed")
        print("   3. Update .env file with the new key")
    else:
        print("⚠️  Unexpected error. Check:")
        print("   - Internet connection")
        print("   - API key validity")
        print("   - Firewall settings")
