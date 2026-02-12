from app.core import security

try:
    print("Testing get_password_hash...")
    pw = "pass123"
    print(f"Input: {pw}")
    hashed = security.get_password_hash(pw)
    print(f"Hashed: {hashed}")
except Exception as e:
    print(f"EXCEPTION: {e}")

try:
    print("\nTesting long password...")
    pw_long = "a" * 100
    print(f"Input length: {len(pw_long)}")
    hashed_long = security.get_password_hash(pw_long)
    print(f"Hashed long: {hashed_long[:20]}...")
except Exception as e:
    print(f"EXCEPTION LONG: {e}")
