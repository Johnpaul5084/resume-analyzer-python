import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("=" * 60)
print("RESUME ANALYZER - END-TO-END TEST")
print("=" * 60)

# Step 1: Login to get token
print("\n📝 Step 1: Logging in...")
login_data = {
    "username": "user9923@test.com",
    "password": "pass123"
}

try:
    response = requests.post(
        f"{BASE_URL}/login/access-token",
        data=login_data,
        timeout=10
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login successful! Token: {token[:20]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Step 2: Create a sample resume text file
print("\n📄 Step 2: Creating sample resume...")
sample_resume = """
JOHN DOE
Email: john.doe@email.com | Phone: (555) 123-4567
LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced Data Analyst with 5 years of expertise in Python, SQL, and data visualization.
Proven track record of delivering actionable insights that drive business decisions.

EXPERIENCE

Senior Data Analyst | Tech Corp | 2021 - Present
- Analyzed large datasets using Python and SQL to identify trends and patterns
- Created interactive dashboards in Tableau for executive leadership
- Improved data processing efficiency by 40% through automation
- Led a team of 3 junior analysts on key projects

Data Analyst | StartUp Inc | 2019 - 2021
- Performed statistical analysis on customer behavior data
- Developed predictive models using machine learning algorithms
- Collaborated with product team to optimize user experience
- Reduced data processing time by 25%

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2015 - 2019
GPA: 3.8/4.0

SKILLS
- Programming: Python, SQL, R
- Tools: Tableau, Power BI, Excel, Jupyter
- Libraries: Pandas, NumPy, Scikit-learn, Matplotlib
- Databases: MySQL, PostgreSQL, MongoDB
- Other: Machine Learning, Statistical Analysis, Data Visualization
"""

# Save to a text file (easier than PDF for testing)
resume_path = Path("sample_resume.txt")
resume_path.write_text(sample_resume)
print(f"✅ Sample resume created: {resume_path}")

# Step 3: Upload resume
print("\n📤 Step 3: Uploading resume for analysis...")
headers = {
    "Authorization": f"Bearer {token}"
}

job_description = """
We are looking for a Senior Data Analyst with strong Python and SQL skills.
Must have experience with data visualization tools like Tableau or Power BI.
Machine learning experience is a plus. Should be able to work with large datasets
and provide actionable insights to stakeholders.
"""

try:
    with open(resume_path, 'rb') as f:
        files = {
            'file': ('sample_resume.txt', f, 'text/plain')
        }
        data = {
            'title': 'Test Resume - Data Analyst',
            'job_description': job_description
        }
        
        print("Sending upload request...")
        response = requests.post(
            f"{BASE_URL}/resumes/upload",
            headers=headers,
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"\n📊 Upload Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ UPLOAD SUCCESSFUL!")
            print("=" * 60)
            
            # Display results
            print(f"\n📋 Resume ID: {result.get('id')}")
            print(f"📝 Title: {result.get('title')}")
            print(f"📊 ATS Score: {result.get('ats_score')}/100")
            
            print("\n📈 Score Breakdown:")
            breakdown = result.get('score_breakdown', {})
            for key, value in breakdown.items():
                print(f"  - {key}: {value}")
            
            print("\n🔍 Missing Keywords:")
            missing = result.get('missing_keywords', [])
            if missing:
                for kw in missing[:10]:
                    print(f"  - {kw}")
            else:
                print("  None")
            
            print("\n🎯 Predicted Role:", result.get('predicted_role', 'N/A'))
            
            print("\n💾 Saving full response to 'upload_test_result.json'...")
            with open('upload_test_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            # Step 4: Test AI Rewrite
            print("\n" + "=" * 60)
            print("🤖 Step 4: Testing AI Rewrite...")
            
            rewrite_data = {
                "text": "I analyzed data using Python and SQL",
                "section_type": "Experience",
                "target_role": "Data Analyst",
                "company_type": "MNC"
            }
            
            rewrite_response = requests.post(
                f"{BASE_URL}/resumes/rewrite",
                headers=headers,
                json=rewrite_data,
                timeout=30
            )
            
            print(f"Rewrite Response Status: {rewrite_response.status_code}")
            
            if rewrite_response.status_code == 200:
                rewritten = rewrite_response.text.strip('"')
                print("\n✅ AI REWRITE SUCCESSFUL!")
                print("\nOriginal:")
                print(f"  {rewrite_data['text']}")
                print("\nRewritten (MNC-Ready):")
                print(f"  {rewritten}")
            else:
                print(f"\n❌ AI Rewrite failed: {rewrite_response.status_code}")
                print(f"Error: {rewrite_response.text}")
            
            print("\n" + "=" * 60)
            print("✅ ALL TESTS COMPLETED!")
            print("=" * 60)
            
        else:
            print(f"\n❌ UPLOAD FAILED!")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Save error for debugging
            with open('upload_error.txt', 'w') as f:
                f.write(f"Status: {response.status_code}\n")
                f.write(f"Response: {response.text}\n")
            
except Exception as e:
    print(f"\n❌ ERROR during upload: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
print("\n🧹 Cleaning up...")
if resume_path.exists():
    resume_path.unlink()
    print("✅ Sample resume file deleted")

print("\n✅ Test complete! Check the output above for any errors.")
