"""Phoenix Test Suite - ASCII output only (no emoji), writes to file"""
import requests, json, os, time, sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

BASE = "http://127.0.0.1:8000/api/v1"
RESULTS = []
TOKEN = None
RID = None

def log(s, ep, d=""):
    ok = "[PASS]" if s=="PASS" else ("[FAIL]" if s=="FAIL" else "[SKIP]")
    line = f"{ok} {ep}"
    if d: line += f"\n       -> {d}"
    print(line)
    RESULTS.append((s, ep, d))

def H():
    h = {}
    if TOKEN: h["Authorization"] = f"Bearer {TOKEN}"
    return h

# 1. ROOT
print("\n--- 1. Root ---")
try:
    r = requests.get("http://127.0.0.1:8000/", timeout=8)
    log("PASS" if r.status_code==200 else "FAIL","GET /",f"HTTP {r.status_code}")
except Exception as e: log("FAIL","GET /",str(e)[:80])

# 2. AUTH
print("\n--- 2. Auth ---")
ts = str(int(time.time()))
u = {"email":f"t{ts}@test.com","password":"Test@12345","full_name":"Test User"}
try:
    r = requests.post(f"{BASE}/signup",json=u,timeout=15)
    log("PASS" if r.status_code in[200,201] else "FAIL","POST /signup",f"HTTP {r.status_code} {r.text[:80]}")
except Exception as e: log("FAIL","POST /signup",str(e)[:80])
try:
    r = requests.post(f"{BASE}/login/access-token",data={"username":u["email"],"password":u["password"]},timeout=15)
    if r.status_code==200: TOKEN=r.json().get("access_token"); log("PASS","POST /login","Token OK")
    else: log("FAIL","POST /login",f"HTTP {r.status_code} {r.text[:80]}")
except Exception as e: log("FAIL","POST /login",str(e)[:80])
try:
    r = requests.get(f"{BASE}/users/me",headers=H(),timeout=10)
    log("PASS" if r.status_code==200 else "FAIL","GET /users/me",f"HTTP {r.status_code}")
except Exception as e: log("FAIL","GET /users/me",str(e)[:80])

# 3. RESUMES
print("\n--- 3. Resumes ---")
if TOKEN:
    txt=b"John Phoenix - Python Dev\nEmail:john@ex.com\nSKILLS:Python,FastAPI,SQL\nEXP:3yrs TechCorp\nEDU:BTech CS"
    try:
        r = requests.post(f"{BASE}/resumes/upload",headers={"Authorization":f"Bearer {TOKEN}"},
            files={"file":("r.txt",txt,"text/plain")},
            data={"title":"Test","job_description":"Python FastAPI dev"},timeout=60)
        if r.status_code==200:
            RID=r.json().get("id")
            log("PASS","POST /resumes/upload",f"ID:{RID} ATS:{r.json().get('ats_score')}")
        else: log("FAIL","POST /resumes/upload",f"HTTP {r.status_code} {r.text[:150]}")
    except Exception as e: log("FAIL","POST /resumes/upload",str(e)[:80])
    try:
        r = requests.get(f"{BASE}/resumes/",headers=H(),timeout=10)
        log("PASS" if r.status_code==200 else "FAIL","GET /resumes/",f"HTTP {r.status_code} Count:{len(r.json()) if r.status_code==200 else '?'}")
    except Exception as e: log("FAIL","GET /resumes/",str(e)[:80])
    if RID:
        try:
            r = requests.get(f"{BASE}/resumes/{RID}",headers=H(),timeout=15)
            log("PASS" if r.status_code==200 else "FAIL",f"GET /resumes/ID",f"HTTP {r.status_code}")
        except Exception as e: log("FAIL","GET /resumes/ID",str(e)[:80])
else: log("SKIP","Resumes","No token")

# 4. AI FEATURES
print("\n--- 4. AI Features ---")
if TOKEN:
    for ep,payload in [
        ("/resumes/rewrite",{"text":"Worked on tasks","section_type":"Experience","target_role":"SWE","company_type":"MNC"}),
        ("/resumes/predict-job",{"text":"Python ML FastAPI developer"}),
        ("/resumes/validate-fit",{"text":"Python dev","target_role":"Data Scientist"}),
    ]:
        try:
            r = requests.post(f"{BASE}{ep}",headers=H(),json=payload,timeout=30)
            log("PASS" if r.status_code==200 else "FAIL",f"POST {ep}",f"HTTP {r.status_code} {r.text[:80] if r.status_code!=200 else 'OK'}")
        except Exception as e: log("FAIL",f"POST {ep}",str(e)[:80])
else: log("SKIP","AI Features","No token")

# 5. CAREER GURU
print("\n--- 5. Career Guru ---")
if TOKEN and RID:
    try:
        r = requests.post(f"{BASE}/career-guru/chat",headers=H(),json={"question":"How to get into Google?","resume_id":RID},timeout=30)
        log("PASS" if r.status_code==200 else "FAIL","POST /career-guru/chat",f"HTTP {r.status_code} {r.text[:100] if r.status_code!=200 else 'Got reply'}")
    except Exception as e: log("FAIL","POST /career-guru/chat",str(e)[:80])
    try:
        r = requests.post(f"{BASE}/career-guru/roadmap",headers=H(),json={"target_role":"ML Engineer","resume_id":RID},timeout=30)
        log("PASS" if r.status_code==200 else "FAIL","POST /career-guru/roadmap",f"HTTP {r.status_code} {r.text[:100] if r.status_code!=200 else 'Got roadmap'}")
    except Exception as e: log("FAIL","POST /career-guru/roadmap",str(e)[:80])
else: log("SKIP","Career Guru","No token or resume")

# 6. JOBS
print("\n--- 6. Jobs ---")
if TOKEN and RID:
    try:
        r = requests.get(f"{BASE}/jobs/recommendations/{RID}",headers=H(),timeout=20)
        log("PASS" if r.status_code==200 else "FAIL",f"GET /jobs/recommendations/ID",f"HTTP {r.status_code} {r.text[:100] if r.status_code!=200 else 'OK'}")
    except Exception as e: log("FAIL","GET /jobs/recommendations/",str(e)[:80])
else: log("SKIP","Jobs","No token or resume")

# REPORT
passed=sum(1 for r in RESULTS if r[0]=="PASS")
failed=sum(1 for r in RESULTS if r[0]=="FAIL")
skipped=sum(1 for r in RESULTS if r[0]=="SKIP")
total=len(RESULTS)
print(f"\n====== FINAL REPORT ======")
print(f"PASSED : {passed}/{total}")
print(f"FAILED : {failed}/{total}")
print(f"SKIPPED: {skipped}/{total}")
print(f"Score  : {round(passed/max(total,1)*100)}%")
if failed:
    print("\nFAILED:")
    for r in RESULTS:
        if r[0]=="FAIL":
            print(f"  -> {r[1]}: {r[2][:100]}")
print("READY FOR DEPLOY!" if failed==0 else "FIX FAILURES BEFORE DEPLOY")

with open("test_results_full.txt","w",encoding="utf-8") as f:
    for r2 in RESULTS:
        f.write(f"[{r2[0]}] {r2[1]}: {r2[2]}\n")
    f.write(f"\nPASSED:{passed} FAILED:{failed} SKIPPED:{skipped} Score:{round(passed/max(total,1)*100)}%\n")
sys.exit(0 if failed==0 else 1)
