import sys
import os
import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app
from database.mongodb import get_users_collection, get_otps_collection

def run_tests():
    print("==================================================")
    print("RUNNING AUTHENTICATION & PROFILE ENHANCEMENT TESTS")
    print("==================================================\n")

    client = app.test_client()

    # Test email & password
    test_email = "test.otp.user@example.com"
    initial_password = "password123"
    new_password = "newpassword456"

    # Clean up test user & OTPs if exist
    users_col = get_users_collection()
    otps_col = get_otps_collection()
    users_col.delete_many({"email": test_email})
    otps_col.delete_many({"email": test_email})

    passed_count = 0
    total_tests = 7

    # 1. Signup Initial Account
    res1 = client.post("/api/auth/signup", json={
        "name": "OTP Test User",
        "email": test_email,
        "password": initial_password,
        "confirm_password": initial_password
    })
    token = None
    if res1.status_code == 201:
        token = res1.get_json().get("token")
        print("[TEST 1] Signup initial test user: PASSED [OK]")
        passed_count += 1
    else:
        print(f"[TEST 1] Signup initial test user: FAILED ({res1.status_code} - {res1.get_json()})")

    # 2. Request Forgot Password OTP
    res2 = client.post("/api/auth/forgot-password", json={"email": test_email})
    if res2.status_code == 200:
        otp_doc = otps_col.find_one({"email": test_email, "used": False})
        if otp_doc and len(otp_doc.get("otp", "")) == 6:
            otp_code = otp_doc["otp"]
            print(f"[TEST 2] Request Forgot Password OTP (Generated OTP: {otp_code}): PASSED [OK]")
            passed_count += 1
        else:
            print("[TEST 2] Request Forgot Password OTP: FAILED (No OTP record generated in DB)")
    else:
        print(f"[TEST 2] Request Forgot Password OTP: FAILED ({res2.status_code})")

    # 3. Verify Invalid & Valid OTP
    res3_invalid = client.post("/api/auth/verify-otp", json={"email": test_email, "otp": "000000"})
    res3_valid = client.post("/api/auth/verify-otp", json={"email": test_email, "otp": otp_code})
    if res3_invalid.status_code == 400 and res3_valid.status_code == 200:
        print("[TEST 3] Verify OTP (Invalid rejected, Valid accepted): PASSED [OK]")
        passed_count += 1
    else:
        print(f"[TEST 3] Verify OTP: FAILED (Invalid status: {res3_invalid.status_code}, Valid status: {res3_valid.status_code})")

    # 4. Reset Password
    res4 = client.post("/api/auth/reset-password", json={
        "email": test_email,
        "otp": otp_code,
        "new_password": new_password,
        "confirm_password": new_password
    })
    if res4.status_code == 200:
        print("[TEST 4] Reset Password with Bcrypt update: PASSED [OK]")
        passed_count += 1
    else:
        print(f"[TEST 4] Reset Password: FAILED ({res4.status_code} - {res4.get_json()})")

    # 5. Login with New Password
    res5_old = client.post("/api/auth/login", json={"email": test_email, "password": initial_password})
    res5_new = client.post("/api/auth/login", json={"email": test_email, "password": new_password})
    if res5_old.status_code == 401 and res5_new.status_code == 200:
        token = res5_new.get_json().get("token")
        print("[TEST 5] Login with New Password (Old rejected, New accepted): PASSED [OK]")
        passed_count += 1
    else:
        print(f"[TEST 5] Login with New Password: FAILED (Old: {res5_old.status_code}, New: {res5_new.status_code})")

    # 6. Profile Retrieval & Update
    res_prof_get = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {token}"})
    res_prof_put = client.put("/api/auth/profile", headers={"Authorization": f"Bearer {token}"}, json={"name": "Updated OTP User"})
    if res_prof_get.status_code == 200 and res_prof_put.status_code == 200:
        print("[TEST 6] GET & PUT Profile endpoints: PASSED [OK]")
        passed_count += 1
    else:
        print(f"[TEST 6] GET & PUT Profile endpoints: FAILED (GET: {res_prof_get.status_code}, PUT: {res_prof_put.status_code})")

    # 7. Google OAuth User 2-Step Signup & Complete Registration
    google_test_email = "google.test.account@example.com"
    users_col.delete_many({"email": google_test_email})
    res7_cb = client.get(f"/api/auth/google/callback?email={google_test_email}&name=Google+OAuth+User&sub=google-id-12345&mode=signup")
    res7_complete = client.post("/api/auth/google/complete-signup", json={
        "email": google_test_email,
        "username": "Google OAuth User",
        "password": "WebsitePassword123",
        "confirm_password": "WebsitePassword123",
        "google_id": "google-id-12345"
    })
    if res7_cb.status_code == 302 and "step=2" in res7_cb.location and res7_complete.status_code == 201:
        g_user = users_col.find_one({"email": google_test_email})
        if g_user and g_user.get("google_id") == "google-id-12345" and g_user.get("password_hash"):
            print("[TEST 7] Google OAuth 2-Step Signup with Website Password: PASSED [OK]")
            passed_count += 1
        else:
            print("[TEST 7] Google OAuth 2-Step Signup: FAILED (User record or password_hash missing)")
    else:
        print(f"[TEST 7] Google OAuth 2-Step Signup: FAILED (Callback: {res7_cb.status_code}, Complete: {res7_complete.status_code})")

    # Clean up test users
    users_col.delete_many({"email": test_email})
    users_col.delete_many({"email": google_test_email})
    otps_col.delete_many({"email": test_email})

    print(f"\nAuth & Profile Test Summary: {passed_count}/{total_tests} tests passed.")

if __name__ == "__main__":
    run_tests()
