import os
import sys
import unittest
import time

sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database.mongodb import Database, get_users_collection
from database.seed import seed_database
from services.auth_service import AuthService

class TestSignInFlow(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        Database.get_db()

    def tearDown(self):
        self.app_context.pop()

    def test_signin_flow_requirements(self):
        print("\n==================================================")
        print("RUNNING SPECIFIC SIGN IN FLOW VERIFICATION TESTS")
        print("==================================================")

        users_col = get_users_collection()
        registered_email = f"registered.user.{int(time.time())}@example.com"
        unregistered_email = f"unregistered.user.{int(time.time())}@example.com"
        password = "SecurePassword123!"
        wrong_password = "WrongPassword999!"

        # Register a user directly in DB for testing Sign In
        password_hash = AuthService.hash_password(password)
        users_col.insert_one({
            "_id": f"user_signin_{int(time.time())}",
            "name": "Registered User",
            "email": registered_email,
            "password_hash": password_hash,
            "auth_provider": "local"
        })

        # --- TEST 1: Registered Email + Correct Password ---
        print("\n[TEST 1] Registered Email + Correct Password Sign In...")
        res1 = self.client.post("/api/auth/login", json={
            "email": registered_email,
            "password": password
        })
        self.assertEqual(res1.status_code, 200, f"Expected 200 OK, got {res1.status_code}: {res1.get_data(as_text=True)}")
        data1 = res1.get_json()
        self.assertIn("token", data1, "JWT token missing from login response")
        print("  -> PASSED [OK]: Login successful, returned JWT token and user profile.")

        # --- TEST 2: Registered Email + Wrong Password ---
        print("\n[TEST 2] Registered Email + Wrong Password Sign In...")
        res2 = self.client.post("/api/auth/login", json={
            "email": registered_email,
            "password": wrong_password
        })
        self.assertEqual(res2.status_code, 401, f"Expected 401 Unauthorized, got {res2.status_code}")
        data2 = res2.get_json()
        self.assertEqual(data2.get("error"), "Incorrect password. Please try again.", f"Unexpected error msg: {data2}")
        print("  -> PASSED [OK]: Displayed exact message 'Incorrect password. Please try again.'")

        # --- TEST 3: Unregistered Email Sign In ---
        print("\n[TEST 3] Unregistered Email Sign In...")
        res3 = self.client.post("/api/auth/login", json={
            "email": unregistered_email,
            "password": password
        })
        self.assertEqual(res3.status_code, 404, f"Expected 404 Not Found, got {res3.status_code}")
        data3 = res3.get_json()
        self.assertEqual(data3.get("error"), "Account not found. Please Sign Up first.", f"Unexpected error msg: {data3}")
        print("  -> PASSED [OK]: Displayed exact message 'Account not found. Please Sign Up first.'")

        # --- TEST 4: Google Sign In with ALREADY Registered Email ---
        print("\n[TEST 4] Google Sign In with ALREADY Registered Email...")
        res4 = self.client.get(f"/api/auth/google/callback?email={registered_email}&name=Registered+User&sub=g12345&mode=login")
        self.assertEqual(res4.status_code, 302, f"Expected 302 Redirect, got {res4.status_code}")
        self.assertIn("/dashboard.html?token=", res4.location, f"Expected redirect to dashboard, got {res4.location}")
        self.assertNotIn("signup.html", res4.location, "Registered user was wrongly redirected to Sign Up!")
        print("  -> PASSED [OK]: Existing Google account signed in directly and redirected to Dashboard!")

        # --- TEST 5: Google Sign In with UNREGISTERED Email ---
        print("\n[TEST 5] Google Sign In with UNREGISTERED Email...")
        res5 = self.client.get(f"/api/auth/google/callback?email={unregistered_email}&name=New+User&sub=g99999&mode=login")
        self.assertEqual(res5.status_code, 302, f"Expected 302 Redirect, got {res5.status_code}")
        self.assertIn("/login.html?error=unregistered_google", res5.location, f"Expected redirect to login error, got {res5.location}")
        self.assertNotIn("signup.html", res5.location, "Unregistered Google user was auto-redirected to Sign Up!")
        
        # Check DB to ensure no new user account was created
        created_user = users_col.find_one({"email": unregistered_email})
        self.assertIsNone(created_user, "Account was created for unregistered Google login attempt!")
        print("  -> PASSED [OK]: Unregistered Google email was NOT created and redirected to Sign In with error notification!")

        # Clean up test user
        users_col.delete_many({"email": registered_email})

        print("\n==================================================")
        print("ALL SIGN IN FLOW TESTS PASSED! [OK]")
        print("==================================================")

if __name__ == "__main__":
    unittest.main()
