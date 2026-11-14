import os
import sys
import unittest
import json
import uuid

# Ensure backend directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from services.ownership_matching_service import (
    OwnershipMatchingService,
    NameMatchingEngine,
    DocumentEntityExtractor,
    DOCUMENT_OWNER_MAP
)
from app import app


class TestDocumentOwnershipMatching(unittest.TestCase):

    def setUp(self):
        self.profile = {
            "id": "usr_test_101",
            "name": "Sri Valli Ch",
            "father_name": "Ravi Ch",
            "mother_name": "Lakshmi Ch",
            "family_member_name": "Suresh Ch",
            "college_name": "JNTU College of Engineering, Hyderabad",
            "course": "B.Tech",
            "branch": "Computer Science and Engineering",
            "roll_number": "21011A0501"
        }

    # -------------------------------------------------------------------------
    # TEST 1: Applicant Document - Correct Owner Matches
    # -------------------------------------------------------------------------
    def test_01_applicant_correct_document(self):
        ocr_text = """
        GOVERNMENT OF INDIA
        Unique Identification Authority of India
        To:
        Sri Valli Ch
        DOB: 15/08/2002
        Female
        1234 5678 9012
        """
        res = OwnershipMatchingService.verify_ownership_and_details(
            document_id="doc_aadhaar",
            service_id="srv_aadhaar",
            application_type="new",
            ocr_text=ocr_text,
            detected_type="aadhaar_card",
            detected_name="Aadhaar Card",
            user_profile=self.profile
        )

        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["ownership_status"], "matched")
        self.assertIn("Matched", res["ownership_label"])
        self.assertEqual(res["owner_category"], "Applicant")
        self.assertIn("XXXX-XXXX-9012", res["extracted_entities"]["masked_aadhaar"])

    # -------------------------------------------------------------------------
    # TEST 2: Applicant Document - Unrelated Person Mismatch
    # -------------------------------------------------------------------------
    def test_02_applicant_unrelated_person_mismatch(self):
        ocr_text = """
        GOVERNMENT OF INDIA
        Unique Identification Authority of India
        To:
        Naveen Kumar G
        DOB: 12/03/1998
        Male
        9876 5432 1098
        """
        res = OwnershipMatchingService.verify_ownership_and_details(
            document_id="doc_aadhaar",
            service_id="srv_aadhaar",
            application_type="new",
            ocr_text=ocr_text,
            detected_type="aadhaar_card",
            detected_name="Aadhaar Card",
            user_profile=self.profile
        )

        self.assertEqual(res["status"], "invalid")
        self.assertEqual(res["ownership_status"], "person_mismatch")
        self.assertIn("The uploaded document does not appear to belong to the registered applicant", res["reason"])
        self.assertIn("Please upload your own document", res["reason"])

    # -------------------------------------------------------------------------
    # TEST 3: Parent Document - Correct Father's Document
    # -------------------------------------------------------------------------
    def test_03_correct_father_aadhaar(self):
        ocr_text = """
        GOVERNMENT OF INDIA
        Unique Identification Authority of India
        Ravi Ch
        DOB: 01/01/1970
        Male
        5555 6666 7777
        """
        res = OwnershipMatchingService.verify_ownership_and_details(
            document_id="doc_father_aadhaar",
            service_id="srv_scholarship",
            application_type="new",
            ocr_text=ocr_text,
            detected_type="father_aadhaar",
            detected_name="Father's Aadhaar Card",
            user_profile=self.profile
        )

        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["ownership_status"], "matched")
        self.assertEqual(res["owner_category"], "Father")
        self.assertIn("Father's document verified", res["reason"])

    # -------------------------------------------------------------------------
    # TEST 4: Parent Document - Applicant Accidentally Uploads Their Own Card
    # -------------------------------------------------------------------------
    def test_04_father_slot_uploaded_applicant_own_card(self):
        ocr_text = """
        GOVERNMENT OF INDIA
        Unique Identification Authority of India
        Sri Valli Ch
        DOB: 15/08/2002
        Female
        1234 5678 9012
        """
        res = OwnershipMatchingService.verify_ownership_and_details(
            document_id="doc_father_aadhaar",
            service_id="srv_scholarship",
            application_type="new",
            ocr_text=ocr_text,
            detected_type="father_aadhaar",
            detected_name="Father's Aadhaar Card",
            user_profile=self.profile
        )

        self.assertEqual(res["status"], "invalid")
        self.assertEqual(res["ownership_status"], "person_mismatch")
        self.assertIn("You uploaded your own document", res["reason"])
        self.assertIn("Father's Aadhaar slot", res["reason"])

    # -------------------------------------------------------------------------
    # TEST 5: Single Initial / Common Surname is NOT Proof of Relationship
    # -------------------------------------------------------------------------
    def test_05_common_initial_not_proof_of_relationship(self):
        # 'Mahesh Ch' has the same initial 'Ch' as 'Ravi Ch' or 'Sri Valli Ch',
        # but is NOT the father and NOT the applicant!
        ocr_text = """
        GOVERNMENT OF INDIA
        Unique Identification Authority of India
        Mahesh Ch
        DOB: 20/05/1975
        Male
        4444 3333 2222
        """
        res = OwnershipMatchingService.verify_ownership_and_details(
            document_id="doc_father_aadhaar",
            service_id="srv_scholarship",
            application_type="new",
            ocr_text=ocr_text,
            detected_type="father_aadhaar",
            detected_name="Father's Aadhaar Card",
            user_profile=self.profile
        )

        self.assertEqual(res["status"], "invalid")
        self.assertEqual(res["ownership_status"], "person_mismatch")
        self.assertIn("does not match the registered Father's details", res["reason"])

    # -------------------------------------------------------------------------
    # TEST 6: College Allotment Order - Correct Student & College Match
    # -------------------------------------------------------------------------
    def test_06_correct_college_allotment(self):
        ocr_text = """
        TELANGANA STATE COUNCIL OF HIGHER EDUCATION
        CONVENER, TS EAMCET ADMISSIONS
        PROVISIONAL ALLOTMENT ORDER
        
        Candidate Name: Sri Valli Ch
        Father's Name: Ravi Ch
        Hall Ticket / Allotment No: 21011A0501
        Alloted College: JNTU College of Engineering, Hyderabad
        Branch / Course: Computer Science and Engineering (CSE), B.Tech
        Academic Year: 2024-2025
        """
        res = OwnershipMatchingService.verify_ownership_and_details(
            document_id="doc_college_allotment",
            service_id="srv_scholarship",
            application_type="new",
            ocr_text=ocr_text,
            detected_type="college_allotment",
            detected_name="College Admission / Allotment Order",
            user_profile=self.profile
        )

        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["ownership_status"], "matched")
        self.assertEqual(res["owner_category"], "College / Educational Institution")
        self.assertIn("Allotment Order verified for student", res["reason"])

    # -------------------------------------------------------------------------
    # TEST 7: College Allotment Order - Different Student Name Mismatch
    # -------------------------------------------------------------------------
    def test_07_college_allotment_student_name_mismatch(self):
        ocr_text = """
        TELANGANA STATE COUNCIL OF HIGHER EDUCATION
        CONVENER, TS EAMCET ADMISSIONS
        PROVISIONAL ALLOTMENT ORDER
        
        Candidate Name: Rajesh Goud B
        Father's Name: Ramulu B
        Hall Ticket / Allotment No: 21099A0402
        Alloted College: JNTU College of Engineering, Hyderabad
        Branch / Course: Computer Science and Engineering (CSE), B.Tech
        """
        res = OwnershipMatchingService.verify_ownership_and_details(
            document_id="doc_college_allotment",
            service_id="srv_scholarship",
            application_type="new",
            ocr_text=ocr_text,
            detected_type="college_allotment",
            detected_name="College Admission / Allotment Order",
            user_profile=self.profile
        )

        self.assertEqual(res["status"], "invalid")
        self.assertEqual(res["ownership_status"], "person_mismatch")
        self.assertIn("Invalid Document – Student Name Mismatch", res["reason"])
        self.assertIn("does not appear to belong to the registered applicant", res["reason"])

    # -------------------------------------------------------------------------
    # TEST 8: Low OCR Clarity / Unreadable Text -> Needs Manual Review
    # -------------------------------------------------------------------------
    def test_08_low_ocr_clarity_needs_manual_review(self):
        ocr_text = "blurry blur blur"
        res = OwnershipMatchingService.verify_ownership_and_details(
            document_id="doc_tenth_memo",
            service_id="srv_caste_cert",
            application_type="new",
            ocr_text=ocr_text,
            detected_type="tenth_memo",
            detected_name="10th / SSC Marks Memo",
            user_profile=self.profile
        )

        self.assertEqual(res["status"], "needs_attention")
        self.assertEqual(res["ownership_status"], "needs_manual_review")
        self.assertIn("Needs Manual Review", res["reason"])

    # -------------------------------------------------------------------------
    # TEST 9: Missing Reference in Profile -> Needs Manual Review (Never Auto Invalid)
    # -------------------------------------------------------------------------
    def test_09_missing_reference_in_profile(self):
        empty_profile = {"id": "usr_guest", "name": ""}
        ocr_text = "Sri Valli Ch DOB 15/08/2002 Female 1234 5678 9012"

        res = OwnershipMatchingService.verify_ownership_and_details(
            document_id="doc_aadhaar",
            service_id="srv_aadhaar",
            application_type="new",
            ocr_text=ocr_text,
            detected_type="aadhaar_card",
            detected_name="Aadhaar Card",
            user_profile=empty_profile
        )

        self.assertEqual(res["status"], "needs_attention")
        self.assertEqual(res["ownership_status"], "needs_manual_review")
        self.assertIn("Needs Manual Review", res["reason"])

    # -------------------------------------------------------------------------
    # TEST 10: Full Verification Pipeline API Endpoint (/api/verification/run)
    # -------------------------------------------------------------------------
    def test_10_pipeline_endpoint_with_ownership_matching(self):
        client = app.test_client()

        # Generate a test session in MongoDB
        session_id = f"test_sess_{uuid.uuid4().hex[:8]}"

        payload = {
            "session_id": session_id,
            "service_id": "srv_aadhaar_card",
            "application_type": "new",
            "applicant_details": self.profile
        }

        resp = client.post("/api/verification/run", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertIn("session", data)
        self.assertIn("document_results", data)
        self.assertGreater(len(data["document_results"]), 0)

        # Check that missing document slots include owner_category
        first_doc = data["document_results"][0]
        self.assertIn("owner_category", first_doc)
        self.assertIn("ownership_status", first_doc)
        self.assertEqual(first_doc["ownership_status"], "missing")


if __name__ == "__main__":
    unittest.main()
