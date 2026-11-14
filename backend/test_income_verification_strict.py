import sys
import os
import io
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
from services.ocr_service import OCRService
from services.auth_service import AuthService
from database.mongodb import get_users_collection

def test_income_certificate_strict_verification():
    print("=" * 70)
    print("TESTING STRICT INCOME CERTIFICATE VERIFICATION & CONSISTENCY")
    print("=" * 70)

    # -----------------------------------------------------------------
    # PART 1: Table-Driven Test for Income Certificate Upload Field
    # -----------------------------------------------------------------
    print("\n--- PART 1: Verification Against Expected Table (Income Slot) ---")

    test_cases_income_slot = [
        {
            "name": "Income Certificate",
            "text": "Government of Andhra Pradesh Revenue Department Income Certificate Application No IC230717883582 This is to certify that annual income from all sources is Rs. 65,000/- per annum Tahsildar",
            "expected_status": "verified",
            "expected_detected": "income_proof"
        },
        {
            "name": "Caste Certificate",
            "text": "Government of Andhra Pradesh Revenue Department Community, Nativity & Date of Birth Certificate Kumari A. Nirisha Priya belongs to Backward Class BC-B Community Tahsildar",
            "expected_status": "invalid_type",
            "expected_detected": "caste_proof"
        },
        {
            "name": "Birth Certificate",
            "text": "Government of Andhra Pradesh Registrar of Births and Deaths Birth Certificate Form No. 5 Date of Birth 12/04/2005 Place of Birth Government Hospital Child Name",
            "expected_status": "invalid_type",
            "expected_detected": "birth_proof"
        },
        {
            "name": "PAN Card",
            "text": "Income Tax Department Govt. of India Permanent Account Number ABCDE1234F Father's Name DOB 01/01/1990",
            "expected_status": "invalid_type",
            "expected_detected": "pan_card"
        },
        {
            "name": "Aadhaar Card",
            "text": "Government of India Unique Identification Authority of India UIDAI 1234 5678 9012 Mera Aadhaar Meri Pehchan",
            "expected_status": "invalid_type",
            "expected_detected": "aadhaar_card"
        },
        {
            "name": "Voter ID Card",
            "text": "Election Commission of India Electoral Photo Identity Card EPIC No XWM2350114 Elector's Name Varshini Priya",
            "expected_status": "invalid_type",
            "expected_detected": "voter_id"
        },
        {
            "name": "Bank Passbook",
            "text": "State Bank of India Savings Bank Passbook Account Number 12345678901 IFSC Code SBIN0001234 Branch Stamp",
            "expected_status": "invalid_type",
            "expected_detected": "bank_passbook"
        },
        {
            "name": "Ration Card",
            "text": "Food and Civil Supplies Department Government of Andhra Pradesh Smart Rice Card Ration Card Fair Price Shop No 1234",
            "expected_status": "invalid_type",
            "expected_detected": "ration_card"
        },
        {
            "name": "Salary Slip",
            "text": "Infosys BPM Limited Salary Slip For Month of Oct 2026 Basic Pay 42000 HRA 16000 Gross Salary 65000 Net Pay 58000 PF Deduction",
            "expected_status": "invalid_type",
            "expected_detected": "salary_slip"
        },
        {
            "name": "Any other unrelated document",
            "text": "Restaurant Dinner Bill Table 4 Paneer Butter Masala Naan Total Rs 450 Thank You Visit Again",
            "expected_status": "invalid_type",
            "expected_detected": "other_unknown"
        },
        {
            "name": "Uncertain / Unreadable document",
            "text": "xyz abc",
            "expected_status": "needs_review",
            "expected_detected": "uncertain"
        },
        {
            "name": "Blurry Income Certificate (Quality check)",
            "text": "Government of Andhra Pradesh Revenue Department Income Certificate Annual Income Rs 60000",
            "expected_status": "poor_quality",
            "expected_detected": "income_proof",
            "quality": {"is_acceptable": False, "blur_score": 35.0, "issues": ["Document image appears blurry"]}
        }
    ]

    for tc in test_cases_income_slot:
        q = tc.get("quality", {"is_acceptable": True, "blur_score": 150.0})
        res = GeminiVerificationService.verify_document(
            required_doc_name="Income Certificate",
            required_doc_description="Income Certificate issued by Tahsildar",
            expected_keywords=["income certificate", "annual income"],
            file_path="sample.pdf",
            ocr_text=tc["text"],
            opencv_quality=q,
            required_doc_type="income_proof",
            original_filename="test_file.pdf"
        )
        assert res["status"] == tc["expected_status"], f"FAIL for {tc['name']}: expected {tc['expected_status']}, got {res['status']}"
        assert res["detected_type"] == tc["expected_detected"], f"FAIL for {tc['name']}: expected detected_type {tc['expected_detected']}, got {res['detected_type']}"
        print(f"PASS: [Income Slot] {tc['name']:35} -> Detected: {res['detected_type']:15} | Status: {res['status']}")

    # -----------------------------------------------------------------
    # PART 2: Strict Matching Rules Across Other Upload Cards
    # -----------------------------------------------------------------
    print("\n--- PART 2: Strict Matching Rules Across Other Upload Cards ---")

    caste_text = "Government of Andhra Pradesh Revenue Department Community, Nativity & Date of Birth Certificate Kumari A. Nirisha Priya belongs to Backward Class BC-B Community Tahsildar"
    income_text = "Government of Andhra Pradesh Revenue Department Income Certificate Annual income Rs 60000 Tahsildar"
    pan_text = "Income Tax Department Govt. of India Permanent Account Number ABCDE1234F"
    aadhaar_text = "Unique Identification Authority of India UIDAI 1234 5678 9012 Mera Aadhaar"
    birth_text = "Registrar of Births and Deaths Birth Certificate Form No 5 Date of Birth Child Name"

    # Caste slot
    r_caste_ok = GeminiVerificationService.verify_document(
        required_doc_name="Caste Certificate", required_doc_type="caste_proof",
        file_path="sample.pdf", ocr_text=caste_text, opencv_quality={"is_acceptable": True}
    )
    assert r_caste_ok["status"] == "verified", f"Caste in Caste slot should be verified: {r_caste_ok}"
    print("PASS: Caste Certificate in Caste slot -> Verified")

    r_caste_wrong = GeminiVerificationService.verify_document(
        required_doc_name="Caste Certificate", required_doc_type="caste_proof",
        file_path="sample.pdf", ocr_text=income_text, opencv_quality={"is_acceptable": True}
    )
    assert r_caste_wrong["status"] == "invalid_type", f"Income in Caste slot should be invalid: {r_caste_wrong}"
    print("PASS: Income Certificate in Caste slot -> Invalid Document Type")

    # PAN slot
    r_pan_ok = GeminiVerificationService.verify_document(
        required_doc_name="PAN Card", required_doc_type="pan_card",
        file_path="sample.pdf", ocr_text=pan_text, opencv_quality={"is_acceptable": True}
    )
    assert r_pan_ok["status"] == "verified", f"PAN in PAN slot should be verified: {r_pan_ok}"
    print("PASS: PAN Card in PAN slot -> Verified")

    r_pan_wrong = GeminiVerificationService.verify_document(
        required_doc_name="PAN Card", required_doc_type="pan_card",
        file_path="sample.pdf", ocr_text=income_text, opencv_quality={"is_acceptable": True}
    )
    assert r_pan_wrong["status"] == "invalid_type", f"Income in PAN slot should be invalid: {r_pan_wrong}"
    print("PASS: Income Certificate in PAN slot -> Invalid Document Type")

    # Birth slot
    r_birth_ok = GeminiVerificationService.verify_document(
        required_doc_name="Birth Certificate", required_doc_type="birth_proof",
        file_path="sample.pdf", ocr_text=birth_text, opencv_quality={"is_acceptable": True}
    )
    assert r_birth_ok["status"] == "verified", f"Birth in Birth slot should be verified: {r_birth_ok}"
    print("PASS: Birth Certificate in Birth slot -> Verified")

    r_birth_wrong = GeminiVerificationService.verify_document(
        required_doc_name="Birth Certificate", required_doc_type="birth_proof",
        file_path="sample.pdf", ocr_text=income_text, opencv_quality={"is_acceptable": True}
    )
    assert r_birth_wrong["status"] == "invalid_type", f"Income in Birth slot should be invalid: {r_birth_wrong}"
    print("PASS: Income Certificate in Birth slot -> Invalid Document Type")

    # -----------------------------------------------------------------
    # PART 3: Actual Files on Disk in uploads/
    # -----------------------------------------------------------------
    print("\n--- PART 3: Testing Actual User Uploaded Files on Disk ---")
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
    f_caste_pdf = os.path.join(uploads_dir, "14ff060e-82b8-4e6a-8856-c561bbef0b69.pdf")
    f_income_pdf = os.path.join(uploads_dir, "3576b99e-3465-44d0-a983-6a2db529293a.pdf")
    f_voter_pdf = os.path.join(uploads_dir, "69fab356-ca02-4cee-8efb-72f23b781b43.pdf")
    f_aadhaar_pdf = os.path.join(uploads_dir, "c85943ec-d614-45eb-bbe2-a9c7c694fb89.pdf")

    if os.path.exists(f_caste_pdf) and os.path.exists(f_income_pdf):
        ocr_caste = OCRService.extract_text(f_caste_pdf).get("extracted_text", "")
        ocr_income = OCRService.extract_text(f_income_pdf).get("extracted_text", "")

        # 3.1 Actual caste certificate in income slot -> MUST BE REJECTED
        r_actual_caste_in_income = GeminiVerificationService.verify_document(
            required_doc_name="Income Certificate", required_doc_type="income_proof",
            file_path=f_caste_pdf, ocr_text=ocr_caste, opencv_quality={"is_acceptable": True, "blur_score": 150},
            original_filename="cast_certificate_.pdf"
        )
        assert r_actual_caste_in_income["status"] == "invalid_type", f"Actual caste in income slot failed: {r_actual_caste_in_income}"
        assert r_actual_caste_in_income["detected_type"] == "caste_proof"
        print(f"PASS: Actual cast_certificate_.pdf in Income slot -> Invalid Document Type (Detected: {r_actual_caste_in_income['detected_name']})")

        # 3.2 Actual income certificate in income slot -> MUST BE VERIFIED
        r_actual_income_in_income = GeminiVerificationService.verify_document(
            required_doc_name="Income Certificate", required_doc_type="income_proof",
            file_path=f_income_pdf, ocr_text=ocr_income, opencv_quality={"is_acceptable": True, "blur_score": 150},
            original_filename="income_certificate_.pdf"
        )
        assert r_actual_income_in_income["status"] == "verified", f"Actual income in income slot failed: {r_actual_income_in_income}"
        assert r_actual_income_in_income["detected_type"] == "income_proof"
        print(f"PASS: Actual income_certificate_.pdf in Income slot -> Verified (Detected: {r_actual_income_in_income['detected_name']})")

        # 3.3 Actual voter ID in income slot -> MUST BE REJECTED
        if os.path.exists(f_voter_pdf):
            ocr_voter = OCRService.extract_text(f_voter_pdf).get("extracted_text", "")
            r_actual_voter_in_income = GeminiVerificationService.verify_document(
                required_doc_name="Income Certificate", required_doc_type="income_proof",
                file_path=f_voter_pdf, ocr_text=ocr_voter, opencv_quality={"is_acceptable": True, "blur_score": 150},
                original_filename="varshini_vote_.pdf"
            )
            assert r_actual_voter_in_income["status"] == "invalid_type"
            print(f"PASS: Actual varshini_vote_.pdf in Income slot -> Invalid Document Type (Detected: {r_actual_voter_in_income['detected_name']})")

    # -----------------------------------------------------------------
    # PART 4: Verification API Endpoint Simulation
    # -----------------------------------------------------------------
    print("\n--- PART 4: API Endpoint /api/verification/run Simulation ---")
    client = app.test_client()

    users_col = get_users_collection()
    user = users_col.find_one({"email": "nirishapriyaarepalli16@gmail.com"})
    user_id = str(user["_id"]) if user else "usr_test"
    token = AuthService.generate_token(user_id, "nirishapriyaarepalli16@gmail.com", "Nirisha Priya")
    headers = {"Authorization": f"Bearer {token}"}

    session_id = f"test_income_strict_{uuid.uuid4().hex[:8]}"

    # Upload actual Caste Certificate to Income Certificate slot
    import pymupdf as fitz
    doc_wrong = fitz.open()
    p = doc_wrong.new_page(width=600, height=800)
    p.draw_rect(fitz.Rect(0, 0, 600, 800), fill=(0.8, 0.8, 0.8))
    p.insert_text((50, 100), "Government of Andhra Pradesh Revenue Department Community, Nativity & Date of Birth Certificate Caste Backward Class BC-B Tahsildar", fontsize=12, color=(0,0,0))
    caste_bytes = doc_wrong.write()
    doc_wrong.close()

    client.post("/api/uploads", data={
        "file": (io.BytesIO(caste_bytes), "my_caste_cert.pdf"),
        "service_id": "srv_gov_doc_verify",
        "document_id": "doc_income_cert",
        "session_id": session_id
    }, headers=headers, content_type="multipart/form-data")

    # Run verification
    run_res = client.post("/api/verification/run", json={"session_id": session_id, "service_id": "srv_gov_doc_verify"}, headers=headers)
    assert run_res.status_code == 200, f"Run returned {run_res.status_code}: {run_res.data}"
    data = run_res.get_json()

    results = data["document_results"]
    income_res = next(r for r in results if r["document_id"] == "doc_income_cert")
    assert income_res["status"] == "invalid_type", f"Caste in Income slot should be invalid_type, got {income_res['status']}"
    assert income_res["detected_type"] == "caste_proof", f"Detected should be caste_proof, got {income_res['detected_type']}"
    assert data["session"]["overall_status"] == "ACTION REQUIRED"
    assert data["session"]["invalid_type_count"] >= 1
    print(f"PASS: API /api/verification/run correctly rejected Caste in Income slot with status: {income_res['status']}")

    print("\n" + "=" * 70)
    print("ALL STRICT INCOME CERTIFICATE VERIFICATION TESTS PASSED (100%)!")
    print("=" * 70)

if __name__ == "__main__":
    test_income_certificate_strict_verification()
