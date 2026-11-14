import sys
import os
import io
import datetime
import uuid

# Ensure utf-8 stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath("backend"))

from app import app
from services.gemini_service import GeminiVerificationService
from services.auth_service import AuthService
from database.mongodb import get_users_collection

def test_simplified_verification():
    print("=" * 60)
    print("TESTING SIMPLIFIED DOCUMENT VERIFICATION (NO NAME MATCHING)")
    print("=" * 60)

    # -------------------------------------------------------------
    # 1. TEST: Document Type Matching & Classification
    # -------------------------------------------------------------
    print("\n--- TEST 1: Document Type Verification ---")

    # 1.1 Correct Caste Certificate uploaded to Caste Certificate slot
    caste_text = "Government of Telangana Tahsildar Office Integrated Community Caste Certificate Sri K. Ramesh S/o Narayana belongs to Backward Class Group B"
    res1 = GeminiVerificationService.verify_document(
        required_doc_name="Caste Certificate",
        required_doc_description="Community / Caste Certificate",
        expected_keywords=["caste certificate", "community"],
        file_path="sample.pdf",
        ocr_text=caste_text,
        opencv_quality={"is_acceptable": True, "blur_score": 150.0},
        required_doc_type="caste_proof",
        original_filename="caste_cert.pdf"
    )
    assert res1["status"] == "verified", f"Expected 'verified', got {res1['status']}"
    assert "Verified" in res1["reason"], f"Unexpected reason: {res1['reason']}"
    print("PASS 1.1: Caste Certificate in Caste slot -> Verified")

    # 1.2 WRONG DOCUMENT: Income Certificate uploaded to Caste Certificate slot
    income_text = "Government of Andhra Pradesh Revenue Department Income Certificate Annual Income Rs 75000 Tahsildar"
    res2 = GeminiVerificationService.verify_document(
        required_doc_name="Caste Certificate",
        required_doc_description="Community / Caste Certificate",
        expected_keywords=["caste certificate", "community"],
        file_path="sample.pdf",
        ocr_text=income_text,
        opencv_quality={"is_acceptable": True, "blur_score": 150.0},
        required_doc_type="caste_proof",
        original_filename="income_cert.pdf"
    )
    assert res2["status"] == "invalid_type", f"Expected 'invalid_type', got {res2['status']}"
    assert "Invalid Document Type" in res2["reason"], f"Unexpected reason: {res2['reason']}"
    assert res2["reason"] == "Invalid Document Type – The uploaded file does not match the selected document. Please upload the correct document."
    print("PASS 1.2: Income Certificate in Caste slot -> Invalid Document Type (Correct prompt message)")

    # 1.3 POOR QUALITY: Blurry Caste Certificate uploaded
    res3 = GeminiVerificationService.verify_document(
        required_doc_name="Caste Certificate",
        required_doc_description="Community / Caste Certificate",
        expected_keywords=["caste certificate", "community"],
        file_path="sample.pdf",
        ocr_text=caste_text,
        opencv_quality={"is_acceptable": False, "blur_score": 35.0, "issues": ["Document image appears blurry"]},
        required_doc_type="caste_proof",
        original_filename="caste_cert_blurry.pdf"
    )
    assert res3["status"] == "poor_quality", f"Expected 'poor_quality', got {res3['status']}"
    assert "Document Quality Issue" in res3["reason"], f"Unexpected reason: {res3['reason']}"
    assert res3["reason"] == "Document Quality Issue – Your uploaded document is blurry or unclear. Please upload a clear and readable document."
    print("PASS 1.3: Blurry document -> Poor Quality (Correct prompt message)")

    # 1.4 INVALID DOCUMENT TYPE: Unrecognized paper uploaded (Needs Review removed)
    res4 = GeminiVerificationService.verify_document(
        required_doc_name="Aadhaar Card",
        required_doc_description="Aadhaar Card",
        expected_keywords=["uidai", "aadhaar"],
        file_path="sample.pdf",
        ocr_text="Random receipt store invoice item 123",
        opencv_quality={"is_acceptable": True, "blur_score": 120.0},
        required_doc_type="aadhaar_card",
        original_filename="random_doc.pdf"
    )
    assert res4["status"] == "invalid_type", f"Expected 'invalid_type', got: {res4['status']}"
    print("PASS 1.4: Random doc in Aadhaar slot -> Invalid Document Type (Needs Review removed)")

    # 1.5 Aadhaar in Father's Aadhaar slot (Accepted as Aadhaar without checking father's name)
    father_adh_text = "Government of India Unique Identification Authority of India UIDAI 9876 5432 1098 Mera Aadhaar Meri Pehchan"
    res5 = GeminiVerificationService.verify_document(
        required_doc_name="Father's Aadhaar Card",
        required_doc_description="Father's Aadhaar",
        expected_keywords=["uidai", "aadhaar"],
        file_path="sample.pdf",
        ocr_text=father_adh_text,
        opencv_quality={"is_acceptable": True, "blur_score": 140.0},
        required_doc_type="father_aadhaar",
        original_filename="father_aadhaar.pdf"
    )
    assert res5["status"] == "verified", f"Expected 'verified', got {res5['status']}"
    print("PASS 1.5: Aadhaar in Father's Aadhaar slot -> Verified (No father name check)")

    # 1.6 PAN Card Verification
    pan_text = "Income Tax Department Govt of India Permanent Account Number ABCDE1234F Signature"
    res6 = GeminiVerificationService.verify_document(
        required_doc_name="PAN Card",
        required_doc_description="PAN Card",
        expected_keywords=["income tax department", "permanent account number"],
        file_path="sample.pdf",
        ocr_text=pan_text,
        opencv_quality={"is_acceptable": True, "blur_score": 160.0},
        required_doc_type="pan_card",
        original_filename="pan_card.pdf"
    )
    assert res6["status"] == "verified", f"Expected 'verified', got {res6['status']}"
    print("PASS 1.6: PAN Card -> Verified")

    # 1.7 10th Marks Memo Verification
    ssc_text = "Board of Secondary Education SSC Marks Memo Secondary School Certificate GPA 9.8 Hall Ticket 123456"
    res7 = GeminiVerificationService.verify_document(
        required_doc_name="10th Marks Memo",
        required_doc_description="SSC Memo",
        expected_keywords=["ssc", "marks memo"],
        file_path="sample.pdf",
        ocr_text=ssc_text,
        opencv_quality={"is_acceptable": True, "blur_score": 130.0},
        required_doc_type="tenth_memo",
        original_filename="tenth_memo.pdf"
    )
    assert res7["status"] == "verified", f"Expected 'verified', got {res7['status']}"
    print("PASS 1.7: 10th Marks Memo -> Verified")

    # 1.8 Bank Passbook Verification
    passbook_text = "State Bank of India Passbook Account No 1234567890 IFSC SBIN0001234 Branch Stamp"
    res8 = GeminiVerificationService.verify_document(
        required_doc_name="Bank Passbook",
        required_doc_description="Bank Passbook",
        expected_keywords=["passbook", "account no", "ifsc"],
        file_path="sample.pdf",
        ocr_text=passbook_text,
        opencv_quality={"is_acceptable": True, "blur_score": 120.0},
        required_doc_type="bank_passbook",
        original_filename="bank_passbook.pdf"
    )
    assert res8["status"] == "verified", f"Expected 'verified', got {res8['status']}"
    print("PASS 1.8: Bank Passbook -> Verified")

    # 1.9 Study and Conduct Certificate Verification
    study_conduct_text = "Zilla Parishad High School Study and Conduct Certificate Bonafide Student Admission No 4567 Class 10th Academic Year 2024-2025 Conduct Good"
    res9 = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_description="Study and Conduct Certificate",
        expected_keywords=["study and conduct certificate", "bonafide certificate", "conduct"],
        file_path="sample.pdf",
        ocr_text=study_conduct_text,
        opencv_quality={"is_acceptable": True, "blur_score": 135.0},
        required_doc_type="study_certificate",
        original_filename="study_and_conduct_certificate.pdf"
    )
    assert res9["status"] == "verified", f"Expected 'verified', got {res9['status']}"
    print("PASS 1.9: Study and Conduct Certificate -> Verified")

    # -------------------------------------------------------------
    # 2. TEST: Full Pipeline Endpoint /api/verification/run
    # -------------------------------------------------------------
    print("\n--- TEST 2: Verification Run API Endpoint ---")
    client = app.test_client()

    users_col = get_users_collection()
    user = users_col.find_one({"email": "nirishapriyaarepalli16@gmail.com"})
    user_id = str(user["_id"]) if user else "usr_test"
    token = AuthService.generate_token(user_id, "nirishapriyaarepalli16@gmail.com", "Nirisha Priya")
    headers = {"Authorization": f"Bearer {token}"}

    session_id = f"test_simple_{uuid.uuid4().hex[:8]}"

    # Upload 1: Valid Aadhaar PDF (contains an unrelated name "Rajesh Kumar")
    import pymupdf as fitz
    doc1 = fitz.open()
    p1 = doc1.new_page(width=600, height=800)
    p1.draw_rect(fitz.Rect(0, 0, 600, 800), color=(0.1, 0.2, 0.5), fill=(0.75, 0.75, 0.75))
    p1.insert_text((50, 100), "Government of India Unique Identification Authority of India UIDAI Aadhaar 1234 5678 9012 Rajesh Kumar Male 01/01/1990", fontsize=12, color=(0,0,0))
    for i in range(10):
        p1.insert_text((50, 130 + i*25), f"Resident Information Line {i}: Official Government Verification Document Content {i*100}", fontsize=11, color=(0,0,0))
    adh_content = doc1.write()
    doc1.close()

    client.post("/api/uploads", data={
        "file": (io.BytesIO(adh_content), "aadhaar_test.pdf"),
        "service_id": "srv_gov_doc_verify",
        "document_id": "doc_aadhaar",
        "session_id": session_id
    }, headers=headers, content_type="multipart/form-data")

    # Upload 2: Valid PAN PDF (contains an unrelated name "Sunil Sharma")
    doc2 = fitz.open()
    p2 = doc2.new_page(width=600, height=800)
    p2.draw_rect(fitz.Rect(0, 0, 600, 800), color=(0.1, 0.2, 0.5), fill=(0.75, 0.75, 0.75))
    p2.insert_text((50, 100), "Income Tax Department Government of India Permanent Account Number ABCDE1234F Sunil Sharma Father Name Ashok Sharma", fontsize=12, color=(0,0,0))
    for i in range(10):
        p2.insert_text((50, 130 + i*25), f"Income Tax Assessment Line {i}: Official Permanent Account Number Card Content {i*100}", fontsize=11, color=(0,0,0))
    pan_content = doc2.write()
    doc2.close()

    client.post("/api/uploads", data={
        "file": (io.BytesIO(pan_content), "pan_test.pdf"),
        "service_id": "srv_gov_doc_verify",
        "document_id": "doc_pan",
        "session_id": session_id
    }, headers=headers, content_type="multipart/form-data")

    # Run verification pipeline
    run_resp = client.post("/api/verification/run", json={
        "session_id": session_id,
        "service_id": "srv_gov_doc_verify"
    }, headers=headers)
    assert run_resp.status_code == 200, f"Verification run failed: {run_resp.get_json()}"

    run_data = run_resp.get_json()
    doc_results = run_data["document_results"]
    session_data = run_data["session"]

    # Verify that BOTH passed without any person/name mismatch!
    for r in doc_results:
        assert r["status"] == "verified", f"Doc {r['document_name']} failed with status {r['status']}: {r['reason']}"
        assert "ownership_status" not in r or r.get("ownership_status") in [None, ""]
        assert "extracted_entities" not in r or r.get("extracted_entities") == {}

    print(f"PASS 2.1: Overall session status: {session_data['overall_status']}")
    print(f"PASS 2.2: Verified count: {session_data['verified_count']}")
    print("PASS 2.3: No name matching performed. Documents with unrelated names successfully verified based on document type and quality!")

    print("\n" + "=" * 60)
    print("ALL SIMPLIFIED VERIFICATION TESTS PASSED SUCCESSFULLY (10/10)!")
    print("=" * 60)

if __name__ == "__main__":
    test_simplified_verification()
