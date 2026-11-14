import sys
import os

# Set UTF-8 encoding for standard output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from services.gemini_service import GeminiVerificationService

def run_tests():
    print("==================================================")
    print("RUNNING DOCUMENT TEXT EXTRACTION MATCHING MATRIX TESTS")
    print("==================================================\n")

    aadhaar_ocr_text = """
    Government of India
    Unique Identification Authority of India
    Rahul Sharma
    DOB: 15/08/1995
    Male
    1234 5678 9012
    Mera Aadhaar, Meri Pehchan
    """

    voter_ocr_text = """
    ELECTION COMMISSION OF INDIA
    ELECTORAL PHOTO IDENTITY CARD
    EPIC No: WBG1234567
    Elector Name: RAHUL SHARMA
    Father's Name: SURESH SHARMA
    Sex: Male / Age: 28
    """

    caste_ocr_text = """
    Government of Andhra Pradesh / Revenue Department
    CASTE CERTIFICATE / COMMUNITY CERTIFICATE
    This is to certify that Rahul Sharma belongs to Backward Class (BC-B) Community.
    Issued by Tahsildar / Revenue Officer
    """

    insurance_ocr_text = """
    Star Health and Allied Insurance Co Ltd
    HEALTH INSURANCE POLICY CERTIFICATE
    Policy Number: P/123456/01/2026/00099
    Insured Name: Rahul Sharma
    Sum Assured: Rs 5,00,000 / Annual Premium Paid
    Valid From: 01/01/2026 to 31/12/2026
    """

    clear_quality = {"is_acceptable": True, "blur_score": 150.0, "issues": []}

    matrix_test_cases = [
        ("MATRIX 1", "Aadhaar Card", "aadhaar_card", aadhaar_ocr_text, "ready", "✅ Proceed", "aadhaar.pdf"),
        ("MATRIX 2", "Aadhaar Card", "aadhaar_card", voter_ocr_text, "invalid", "❌ Not Found", "voter_card.pdf"),
        ("MATRIX 3", "Voter Card", "voter_id", voter_ocr_text, "ready", "✅ Proceed", "vote.pdf"),
        ("MATRIX 4", "Voter Card", "voter_id", aadhaar_ocr_text, "invalid", "❌ Not Found", "aadhaar.pdf"),
        ("MATRIX 5", "Caste Certificate", "caste_proof", caste_ocr_text, "ready", "✅ Proceed", "caste.pdf"),
        ("MATRIX 6", "Caste Certificate", "caste_proof", insurance_ocr_text, "invalid", "❌ Not Found", "insurance.pdf"),
        ("MATRIX 7", "Insurance Certificate", "insurance_policy", insurance_ocr_text, "ready", "✅ Proceed", "insurance.pdf"),
        ("MATRIX 8", "Insurance Certificate", "insurance_policy", caste_ocr_text, "invalid", "❌ Not Found", "caste.pdf"),
        ("MATRIX 9", "Aadhaar Card", "aadhaar_card", "", "invalid", "❌ Not Found", "vote.pdf")
    ]

    passed_count = 0
    print("| Test ID  | Required Document     | Uploaded Document (OCR) | Expected Result | Actual Result | Status    |")
    print("| -------- | --------------------- | ----------------------- | --------------- | ------------- | --------- |")

    for test_id, req_name, req_type, ocr_text, expected_status, expected_result_code, filename in matrix_test_cases:
        res = GeminiVerificationService._heuristic_classification(
            required_doc_name=req_name,
            expected_category=req_type,
            expected_keywords=[],
            ocr_text=ocr_text,
            opencv_quality=clear_quality,
            fallback_reason="Matrix Test Execution",
            original_filename=filename
        )
        actual_status = res.get("status")
        detected_name = res.get("detected_name", "Unknown")
        actual_result_code = res.get("result_code", "N/A")

        is_pass = (actual_status == expected_status) and (actual_result_code == expected_result_code)
        if is_pass:
            passed_count += 1
            status_str = "PASSED [OK]"
        else:
            status_str = f"FAILED [FAIL] (expected {expected_status}/{expected_result_code}, got {actual_status}/{actual_result_code})"

        print(f"| {test_id:8} | {req_name:21} | {detected_name:23} | {expected_result_code:15} | {actual_result_code:13} | {status_str:9} |")

    print("\n==================================================")
    print(f"Matrix Test Summary: {passed_count}/{len(matrix_test_cases)} tests passed.")
    print("==================================================\n")

if __name__ == "__main__":
    run_tests()
