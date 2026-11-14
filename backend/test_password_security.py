import os
import sys
import unittest
import uuid

# Ensure backend directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from services.auth_service import AuthService
from database.mongodb import get_users_collection
from app import app


class TestPasswordSecurityAndValidation(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    # -------------------------------------------------------------------------
    # TEST 1: Unit Validation of All 5 Strong Password Rules
    # -------------------------------------------------------------------------
    def test_01_strong_password_rules(self):
        # 1. Too short (< 8 chars)
        ok, missing = AuthService.validate_strong_password("Ab1@")
        self.assertFalse(ok)
        self.assertIn("At least 8 characters", missing)

        # 2. Missing uppercase
        ok, missing = AuthService.validate_strong_password("secure@1234")
        self.assertFalse(ok)
        self.assertIn("At least one uppercase letter (A–Z)", missing)

        # 3. Missing lowercase
        ok, missing = AuthService.validate_strong_password("SECURE@1234")
        self.assertFalse(ok)
        self.assertIn("At least one lowercase letter (a–z)", missing)

        # 4. Missing number
        ok, missing = AuthService.validate_strong_password("SecurePassword@")
        self.assertFalse(ok)
        self.assertIn("At least one number (0–9)", missing)

        # 5. Missing special character
        ok, missing = AuthService.validate_strong_password("SecurePassword123")
        self.assertFalse(ok)
        self.assertIn("At least one special character (@, #, $, %, &, !, etc.)", missing)

        # 6. Completely strong password satisfying all 5 criteria
        ok, missing = AuthService.validate_strong_password("SecurePass@2026!")
        self.assertTrue(ok)
        self.assertEqual(len(missing), 0)

    # -------------------------------------------------------------------------
    # TEST 2: Signup Endpoint Rejects Weak Password (< 8 characters)
    # -------------------------------------------------------------------------
    def test_02_signup_rejects_short_password(self):
        payload = {
            "name": "Test User",
            "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Ab1",
            "confirm_password": "Ab1"
        }
        resp = self.client.post("/api/auth/signup", json=payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn("Your password is not strong enough. Please create a stronger password.", data["error"])
        self.assertIn("missing_requirements", data)
        self.assertIn("At least 8 characters", data["missing_requirements"])

    # -------------------------------------------------------------------------
    # TEST 3: Signup Endpoint Rejects Password Missing Numbers/Specials
    # -------------------------------------------------------------------------
    def test_03_signup_rejects_missing_special_and_number(self):
        payload = {
            "name": "Test User",
            "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
            "password": "PasswordOnly",
            "confirm_password": "PasswordOnly"
        }
        resp = self.client.post("/api/auth/signup", json=payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn("Your password is not strong enough. Please create a stronger password.", data["error"])
        self.assertIn("At least one number (0–9)", data["missing_requirements"])
        self.assertIn("At least one special character (@, #, $, %, &, !, etc.)", data["missing_requirements"])

    # -------------------------------------------------------------------------
    # TEST 4: Signup Endpoint Accepts Strong Password and Verifies Bcrypt Hashing
    # -------------------------------------------------------------------------
    def test_04_signup_accepts_strong_password_and_hashes(self):
        unique_email = f"secure_{uuid.uuid4().hex[:6]}@example.com"
        strong_pass = "ValliSecure@2026!"

        payload = {
            "name": "Sri Valli",
            "email": unique_email,
            "password": strong_pass,
            "confirm_password": strong_pass
        }
        resp = self.client.post("/api/auth/signup", json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn("token", data)
        self.assertIn("user", data)

        # Verify MongoDB storage: password_hash must start with $2b$ and plain text must NOT be stored
        users_col = get_users_collection()
        user_in_db = users_col.find_one({"email": unique_email})
        self.assertIsNotNone(user_in_db)
        self.assertNotIn("password", user_in_db)
        self.assertTrue(user_in_db["password_hash"].startswith("$2b$"))

        # Verify password verification works
        self.assertTrue(AuthService.check_password(strong_pass, user_in_db["password_hash"]))
        self.assertFalse(AuthService.check_password("WrongPassword123!", user_in_db["password_hash"]))

    # -------------------------------------------------------------------------
    # TEST 5: Login with Strong Password Succeeds
    # -------------------------------------------------------------------------
    def test_05_login_with_strong_password(self):
        unique_email = f"login_{uuid.uuid4().hex[:6]}@example.com"
        strong_pass = "ComplexPass#9988"

        # Sign up first
        self.client.post("/api/auth/signup", json={
            "name": "Login Test User",
            "email": unique_email,
            "password": strong_pass,
            "confirm_password": strong_pass
        })

        # Test login
        login_resp = self.client.post("/api/auth/login", json={
            "email": unique_email,
            "password": strong_pass
        })
        self.assertEqual(login_resp.status_code, 200)
        login_data = login_resp.get_json()
        self.assertIn("token", login_data)
        self.assertEqual(login_data["user"]["email"], unique_email)


if __name__ == "__main__":
    unittest.main()
