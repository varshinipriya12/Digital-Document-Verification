import sys
import os
import io
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app
from database.mongodb import get_uploads_collection, get_verification_results_collection, get_verification_sessions_collection

class TestReplaceFunctionality(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.uploads_col = get_uploads_collection()
        self.results_col = get_verification_results_collection()
        self.sessions_col = get_verification_sessions_collection()
        self.session_id = "test_replace_suite_sess"

    def tearDown(self):
        self.uploads_col.delete_many({"session_id": self.session_id})
        self.results_col.delete_many({"session_id": self.session_id})
        self.sessions_col.delete_many({"session_id": self.session_id})

    def test_replace_across_services(self):
        services = [
            ("srv_income_cert", "doc_salary_slip", "salary_v1.pdf", "salary_v2_replaced.pdf"),
            ("srv_caste_cert", "doc_caste_cert", "caste_v1.pdf", "caste_v2_replaced.pdf"),
            ("srv_birth_cert", "doc_birth_cert", "birth_v1.pdf", "birth_v2_replaced.pdf"),
            ("srv_aadhaar_card", "doc_aadhaar", "aadhaar_v1.pdf", "aadhaar_v2_replaced.pdf"),
            ("srv_pan_card", "doc_pan", "pan_v1.pdf", "pan_v2_replaced.pdf"),
            ("srv_voter_id", "doc_voter_id", "voter_v1.pdf", "voter_v2_replaced.pdf"),
            ("srv_scholarship", "doc_tenth_memo", "tenth_v1.pdf", "tenth_v2_replaced.pdf"),
            ("srv_ration_card", "doc_ration_card", "ration_v1.pdf", "ration_v2_replaced.pdf"),
            ("srv_gov_doc_verify", "doc_address_proof", "address_v1.pdf", "address_v2_replaced.pdf")
        ]

        for srv_id, doc_id, file1_name, file2_name in services:
            # 1. Initial Upload
            resp1 = self.client.post("/api/uploads", data={
                "service_id": srv_id,
                "document_id": doc_id,
                "session_id": self.session_id,
                "file": (io.BytesIO(b"%PDF-1.4 initial content for " + doc_id.encode()), file1_name)
            }, content_type="multipart/form-data")
            self.assertEqual(resp1.status_code, 201, f"Initial upload failed for {srv_id} - {doc_id}")
            data1 = resp1.get_json()
            self.assertEqual(data1["upload"]["original_filename"], file1_name)

            # Check DB has exactly 1 upload for this doc_id
            docs = list(self.uploads_col.find({"session_id": self.session_id, "document_id": doc_id}))
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]["original_filename"], file1_name)

            # 2. Replace Upload (Simulating user clicking 'Replace' and choosing new file)
            resp2 = self.client.post("/api/uploads", data={
                "service_id": srv_id,
                "document_id": doc_id,
                "session_id": self.session_id,
                "file": (io.BytesIO(b"%PDF-1.4 replaced content for " + doc_id.encode()), file2_name)
            }, content_type="multipart/form-data")
            self.assertEqual(resp2.status_code, 201, f"Replace upload failed for {srv_id} - {doc_id}")
            data2 = resp2.get_json()
            self.assertEqual(data2["upload"]["original_filename"], file2_name)

            # Check DB still has exactly 1 upload for this doc_id, now updated to file2_name
            docs2 = list(self.uploads_col.find({"session_id": self.session_id, "document_id": doc_id}))
            self.assertEqual(len(docs2), 1, f"Duplicate found after replace for {srv_id} - {doc_id}")
            self.assertEqual(docs2[0]["original_filename"], file2_name)

            # 3. Test Delete / Remove Slot
            upload_id = data2["upload"]["upload_id"]
            resp3 = self.client.delete(f"/api/uploads/{upload_id}")
            self.assertEqual(resp3.status_code, 200)

            # Check DB has 0 uploads after remove
            docs3 = list(self.uploads_col.find({"session_id": self.session_id, "document_id": doc_id}))
            self.assertEqual(len(docs3), 0)

if __name__ == "__main__":
    unittest.main()
