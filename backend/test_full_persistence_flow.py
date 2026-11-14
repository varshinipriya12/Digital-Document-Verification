import os
import sys
import json
import time
import datetime
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database.mongodb import Database, DB_FILE, get_users_collection, get_verification_sessions_collection, get_verification_results_collection
from database.seed import seed_database

class TestFullPersistenceFlow(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Clean test db file if exists to start fresh
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

        # Force database reset and re-seed
        Database.db = None
        Database.get_db()
        seed_database()

    def tearDown(self):
        self.app_context.pop()

    def test_end_to_end_user_persistence_and_history(self):
        print("\n==================================================")
        print("RUNNING END-TO-END USER PERSISTENCE & HISTORY TESTS")
        print("==================================================")

        test_email = f"persistence.user.{int(time.time())}@example.com"
        test_password = "SecretPassword123!"
        test_name = "Persistence Test User"

        # Step 1: User Sign Up
        print("\n[STEP 1] Testing User Sign Up...")
        signup_resp = self.client.post("/api/auth/signup", json={
            "email": test_email,
            "password": test_password,
            "full_name": test_name
        })
        self.assertEqual(signup_resp.status_code, 201, f"Signup failed: {signup_resp.get_data(as_text=True)}")
        signup_data = signup_resp.get_json()
        token = signup_data["token"]
        user_id = signup_data["user"]["id"]
        print(f"  -> Sign Up successful. Created User ID: {user_id}")

        # Check bcrypt hashing in DB
        users_col = get_users_collection()
        stored_user = users_col.find_one({"email": test_email})
        self.assertIsNotNone(stored_user)
        self.assertTrue(stored_user["password_hash"].startswith("$2b$") or stored_user["password_hash"].startswith("$2a$"), "Password is not bcrypt hashed")
        self.assertNotEqual(stored_user["password_hash"], test_password, "Plaintext password stored!")
        print("  -> Verified password is securely hashed with Bcrypt.")

        # Step 2: Restart Server Simulation (Reset DB memory)
        print("\n[STEP 2] Simulating Server Restart (Clearing RAM memory and reloading from disk)...")
        Database.db = None
        Database.get_db()

        # Step 3: Sign In after Server Restart
        print("\n[STEP 3] Testing Sign In with persisted credentials...")
        login_resp = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        self.assertEqual(login_resp.status_code, 200, f"Login failed after restart: {login_resp.get_data(as_text=True)}")
        login_data = login_resp.get_json()
        token = login_data["token"]
        print("  -> Sign In successful! User credentials persisted across server restart.")

        # Step 4: Perform Verification Session 1
        print("\n[STEP 4] Executing Verification Session #1...")
        session_id_1 = f"session_1_{int(time.time())}"
        headers = {"Authorization": f"Bearer {token}"}

        # Upload document for session 1
        upload_resp_1 = self.client.post("/api/uploads/upload", data={
            "session_id": session_id_1,
            "service_id": "income-certificate",
            "document_id": "income_aadhaar"
        }, content_type='multipart/form-data', headers=headers)
        
        # Run verification 1
        run_resp_1 = self.client.post("/api/verification/run", json={
            "session_id": session_id_1,
            "service_id": "income-certificate"
        }, headers=headers)
        self.assertEqual(run_resp_1.status_code, 200, f"Run verification 1 failed: {run_resp_1.get_data(as_text=True)}")
        print(f"  -> Verification Session #1 completed. Session ID: {session_id_1}")

        # Step 5: Perform Verification Session 2 (Multiple Sessions)
        print("\n[STEP 5] Executing Verification Session #2 (Multiple verifications test)...")
        session_id_2 = f"session_2_{int(time.time())}"
        
        run_resp_2 = self.client.post("/api/verification/run", json={
            "session_id": session_id_2,
            "service_id": "income-certificate"
        }, headers=headers)
        self.assertEqual(run_resp_2.status_code, 200, f"Run verification 2 failed: {run_resp_2.get_data(as_text=True)}")
        print(f"  -> Verification Session #2 completed. Session ID: {session_id_2}")

        # Step 6: Restart Server Simulation #2
        print("\n[STEP 6] Simulating 2nd Server Restart...")
        Database.db = None
        Database.get_db()

        # Step 7: Fetch My Verifications History
        print("\n[STEP 7] Fetching My Verifications History after Server Restart...")
        history_resp = self.client.get("/api/verification/my-verifications", headers=headers)
        self.assertEqual(history_resp.status_code, 200, f"Get history failed: {history_resp.get_data(as_text=True)}")
        history_data = history_resp.get_json()
        verifications = history_data.get("verifications", [])
        
        self.assertGreaterEqual(len(verifications), 2, f"Expected at least 2 sessions, got {len(verifications)}")
        session_ids_retrieved = [v["session_id"] for v in verifications]
        self.assertIn(session_id_1, session_ids_retrieved, "Session 1 missing from history")
        self.assertIn(session_id_2, session_ids_retrieved, "Session 2 missing from history")
        print(f"  -> All {len(verifications)} verification sessions preserved and retrieved successfully!")

        # Verify document breakdown in history item
        sess1_item = next(v for v in verifications if v["session_id"] == session_id_1)
        self.assertIn("documents", sess1_item, "Document breakdown missing from history")
        print(f"  -> Document breakdown included in history: {len(sess1_item['documents'])} documents listed.")

        # Step 8: Strict User Privacy & Data Isolation Test
        print("\n[STEP 8] Testing Strict User Privacy & Data Isolation...")
        test_email_b = f"user.b.{int(time.time())}@example.com"
        signup_b = self.client.post("/api/auth/signup", json={
            "email": test_email_b,
            "password": test_password,
            "full_name": "User B"
        })
        token_b = signup_b.get_json()["token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User B fetches my-verifications
        hist_b = self.client.get("/api/verification/my-verifications", headers=headers_b).get_json()
        self.assertEqual(len(hist_b["verifications"]), 0, "User B can see User A's history!")

        # User B attempts to view User A's report directly
        unauth_report_resp = self.client.get(f"/api/verification/results/{session_id_1}", headers=headers_b)
        self.assertEqual(unauth_report_resp.status_code, 403, "User B was not blocked from viewing User A's report!")
        print("  -> Data isolation verified: User B cannot access User A's history or reports.")

        print("\n==================================================")
        print("ALL END-TO-END PERSISTENCE & HISTORY TESTS PASSED! [OK]")
        print("==================================================")

if __name__ == "__main__":
    unittest.main()
