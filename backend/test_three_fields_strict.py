import sys
import os
import cv2
import numpy as np

# Ensure utf-8 stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath("backend"))

from services.gemini_service import GeminiVerificationService
from services.opencv_service import OpenCVQualityChecker

def create_sample_photo(filename, blur=False, dark=False):
    """Generate a synthetic test photograph with skin tones and valid portrait aspect ratio."""
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    
    if dark:
        img = np.full((400, 300, 3), (25, 25, 25), dtype=np.uint8)
    else:
        # 300x400 (aspect ratio 1.33) portrait photo with light background
        img = np.full((400, 300, 3), (235, 235, 235), dtype=np.uint8)
        # Add facial region with natural human skin tones in BGR (approx 150, 180, 220)
        img[80:290, 75:225] = (150, 180, 220)
        
    if blur:
        img = cv2.GaussianBlur(img, (45, 45), 0)
        
    cv2.imwrite(filepath, img)
    return filepath

def run_all_tests():
    print("=" * 75)
    print("TESTING STRICT VERIFICATION FOR EXACTLY THREE DOCUMENT FIELDS:")
    print("1. Passport Size Photo")
    print("2. Study and Conduct Certificate")
    print("3. Intermediate Marks Memo")
    print("=" * 75)

    clear_quality = {"is_acceptable": True, "blur_score": 150.0}
    blurry_quality = {"is_acceptable": False, "blur_score": 35.0, "issues": ["Document image appears blurry"]}

    # Pre-generate sample test images
    valid_photo_path = create_sample_photo("test_valid_passport_photo.jpg")
    blurry_photo_path = create_sample_photo("test_blurry_passport_photo.jpg", blur=True)
    dark_photo_path = create_sample_photo("test_dark_passport_photo.jpg", dark=True)

    # Standard OCR Text Samples for Each Document Type
    pan_text = "INCOME TAX DEPARTMENT GOVT OF INDIA PERMANENT ACCOUNT NUMBER ABCDE1234F SRI RAMESH FATHER NAME SIGNATURE"
    aadhaar_text = "GOVERNMENT OF INDIA UNIQUE IDENTIFICATION AUTHORITY OF INDIA UIDAI 1234 5678 9012 MERA AADHAAR MERI PEHCHAN"
    caste_text = "GOVERNMENT OF TELANGANA REVENUE DEPARTMENT TAHSILDAR OFFICE CASTE CERTIFICATE SRI KUMAR BELONGS TO BACKWARD CLASS GROUP B"
    income_text = "GOVERNMENT OF ANDHRA PRADESH REVENUE DEPARTMENT TAHSILDAR INCOME CERTIFICATE ANNUAL INCOME FROM ALL SOURCES RS 75000 PER ANNUM"
    birth_text = "MUNICIPAL CORPORATION FORM NO 5 BIRTH CERTIFICATE REGISTER OF BIRTHS AND DEATHS PLACE OF BIRTH HYDERABAD DATE OF BIRTH 15/08/2004"
    tenth_memo_text = "BOARD OF SECONDARY EDUCATION ANDHRA PRADESH SECONDARY SCHOOL CERTIFICATE SSC PUBLIC EXAMINATIONS MARKS MEMORANDUM GPA 9.8 ROLL NO 123456"
    inter_memo_text = "BOARD OF INTERMEDIATE EDUCATION TELANGANA STATE INTERMEDIATE PUBLIC EXAMINATION MARKS MEMORANDUM ENGLISH MATHEMATICS PHYSICS CHEMISTRY TOTAL MARKS 980/1000 RESULT PASS A GRADE"
    tenth_study_text = "ZILLA PARISHAD HIGH SCHOOL STUDY AND CONDUCT CERTIFICATE THIS IS TO CERTIFY THAT MASTER KUMAR WAS A BONAFIDE STUDENT OF CLASS 10TH CONDUCT IS GOOD"
    inter_study_text = "SRI CHAITANYA JUNIOR COLLEGE STUDY AND CONDUCT CERTIFICATE THIS IS TO CERTIFY THAT MS SITA WAS A BONAFIDE STUDENT OF INTERMEDIATE MPC 2ND YEAR CONDUCT IS GOOD"
    other_text = "ABC ELECTRONICS PRIVATE LIMITED INVOICE BILL NUMBER 98765 TOTAL AMOUNT RS 5400 PAID CASH"

    # =========================================================================
    # PART 1: PASSPORT SIZE PHOTO VERIFICATION TESTS
    # =========================================================================
    print("\n--- PART 1: Passport Size Photo Field ---")

    # 1.1 Valid Passport Size Photograph -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Passport Size Photo",
        required_doc_type="passport_photo",
        file_path=valid_photo_path,
        ocr_text="",
        opencv_quality=clear_quality,
        original_filename="passport_photo.jpg"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}: {r['reason']}"
    print("PASS 1.1: Valid Passport Size Photograph -> ACCEPT (Verified)")

    # 1.2 Blurry Photograph -> REJECT / POOR QUALITY
    r = GeminiVerificationService.verify_document(
        required_doc_name="Passport Size Photo",
        required_doc_type="passport_photo",
        file_path=blurry_photo_path,
        ocr_text="",
        opencv_quality=blurry_quality,
        original_filename="blurry_passport_photo.jpg"
    )
    assert r["status"] == "poor_quality", f"Expected 'poor_quality', got {r['status']}: {r['reason']}"
    assert "Document Quality Issue" in r["reason"]
    print("PASS 1.2: Blurry Photograph -> POOR QUALITY (Correct Quality Issue Message)")

    # 1.3 PAN Card in Photo slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Passport Size Photo",
        required_doc_type="passport_photo",
        file_path="pan.pdf",
        ocr_text=pan_text,
        opencv_quality=clear_quality,
        original_filename="pan_card.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    assert "Invalid Document Type" in r["reason"]
    print("PASS 1.3: PAN Card in Photo slot -> REJECT (Invalid Document Type)")

    # 1.4 Aadhaar Card in Photo slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Passport Size Photo",
        required_doc_type="passport_photo",
        file_path="aadhaar.pdf",
        ocr_text=aadhaar_text,
        opencv_quality=clear_quality,
        original_filename="aadhaar_card.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 1.4: Aadhaar Card in Photo slot -> REJECT (Invalid Document Type)")

    # 1.5 Caste Certificate in Photo slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Passport Size Photo",
        required_doc_type="passport_photo",
        file_path="caste.pdf",
        ocr_text=caste_text,
        opencv_quality=clear_quality,
        original_filename="caste_certificate.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 1.5: Caste Certificate in Photo slot -> REJECT (Invalid Document Type)")

    # 1.6 Income Certificate in Photo slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Passport Size Photo",
        required_doc_type="passport_photo",
        file_path="income.pdf",
        ocr_text=income_text,
        opencv_quality=clear_quality,
        original_filename="income_certificate.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 1.6: Income Certificate in Photo slot -> REJECT (Invalid Document Type)")

    # 1.7 Birth Certificate in Photo slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Passport Size Photo",
        required_doc_type="passport_photo",
        file_path="birth.pdf",
        ocr_text=birth_text,
        opencv_quality=clear_quality,
        original_filename="birth_certificate.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 1.7: Birth Certificate in Photo slot -> REJECT (Invalid Document Type)")

    # 1.8 10th Marks Memo in Photo slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Passport Size Photo",
        required_doc_type="passport_photo",
        file_path="tenth_memo.pdf",
        ocr_text=tenth_memo_text,
        opencv_quality=clear_quality,
        original_filename="tenth_marks_memo.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 1.8: 10th Marks Memo in Photo slot -> REJECT (Invalid Document Type)")

    # 1.9 Any other document in Photo slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Passport Size Photo",
        required_doc_type="passport_photo",
        file_path="other.pdf",
        ocr_text=other_text,
        opencv_quality=clear_quality,
        original_filename="other_doc.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 1.9: Any other document in Photo slot -> REJECT (Invalid Document Type)")

    # =========================================================================
    # PART 2: STUDY AND CONDUCT CERTIFICATE VERIFICATION TESTS
    # =========================================================================
    print("\n--- PART 2: Study and Conduct Certificate Field ---")

    # 2.1 10th Study and Conduct Certificate -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_type="study_certificate",
        file_path="10th_study.pdf",
        ocr_text=tenth_study_text,
        opencv_quality=clear_quality,
        original_filename="10th_study_and_conduct_certificate.pdf"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}: {r['reason']}"
    print("PASS 2.1: 10th Study and Conduct Certificate -> ACCEPT (Verified)")

    # 2.2 Intermediate Study and Conduct Certificate -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_type="study_certificate",
        file_path="inter_study.pdf",
        ocr_text=inter_study_text,
        opencv_quality=clear_quality,
        original_filename="intermediate_study_and_conduct_certificate.pdf"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}: {r['reason']}"
    print("PASS 2.2: Intermediate Study and Conduct Certificate -> ACCEPT (Verified)")

    # 2.3 PAN Card in Study & Conduct slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_type="study_certificate",
        file_path="pan.pdf",
        ocr_text=pan_text,
        opencv_quality=clear_quality,
        original_filename="pan_card.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    assert "Invalid Document Type" in r["reason"]
    print("PASS 2.3: PAN Card in Study & Conduct slot -> REJECT (Invalid Document Type)")

    # 2.4 Aadhaar Card in Study & Conduct slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_type="study_certificate",
        file_path="aadhaar.pdf",
        ocr_text=aadhaar_text,
        opencv_quality=clear_quality,
        original_filename="aadhaar_card.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 2.4: Aadhaar Card in Study & Conduct slot -> REJECT (Invalid Document Type)")

    # 2.5 10th Marks Memo in Study & Conduct slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_type="study_certificate",
        file_path="tenth_memo.pdf",
        ocr_text=tenth_memo_text,
        opencv_quality=clear_quality,
        original_filename="10th_marks_memo.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 2.5: 10th Marks Memo in Study & Conduct slot -> REJECT (Invalid Document Type)")

    # 2.6 Intermediate Marks Memo in Study & Conduct slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_type="study_certificate",
        file_path="inter_memo.pdf",
        ocr_text=inter_memo_text,
        opencv_quality=clear_quality,
        original_filename="intermediate_marks_memo.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 2.6: Intermediate Marks Memo in Study & Conduct slot -> REJECT (Invalid Document Type)")

    # 2.7 Income Certificate in Study & Conduct slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_type="study_certificate",
        file_path="income.pdf",
        ocr_text=income_text,
        opencv_quality=clear_quality,
        original_filename="income_certificate.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 2.7: Income Certificate in Study & Conduct slot -> REJECT (Invalid Document Type)")

    # 2.8 Any other document in Study & Conduct slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_type="study_certificate",
        file_path="other.pdf",
        ocr_text=other_text,
        opencv_quality=clear_quality,
        original_filename="other_doc.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 2.8: Any other document in Study & Conduct slot -> REJECT (Invalid Document Type)")

    # 2.9 Blurry 10th Study & Conduct Certificate -> POOR QUALITY
    r = GeminiVerificationService.verify_document(
        required_doc_name="Study and Conduct Certificate",
        required_doc_type="study_certificate",
        file_path="10th_study_blurry.pdf",
        ocr_text=tenth_study_text,
        opencv_quality=blurry_quality,
        original_filename="10th_study_blurry.pdf"
    )
    assert r["status"] == "poor_quality", f"Expected 'poor_quality', got {r['status']}: {r['reason']}"
    print("PASS 2.9: Blurry Study & Conduct Certificate -> POOR QUALITY (Correct Quality Issue Message)")

    # =========================================================================
    # PART 3: INTERMEDIATE MARKS MEMO VERIFICATION TESTS
    # =========================================================================
    print("\n--- PART 3: Intermediate Marks Memo Field ---")

    # 3.1 Intermediate Marks Memo -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Intermediate Marks Memo",
        required_doc_type="intermediate_memo",
        file_path="inter_memo.pdf",
        ocr_text=inter_memo_text,
        opencv_quality=clear_quality,
        original_filename="intermediate_marks_memo.pdf"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}: {r['reason']}"
    print("PASS 3.1: Intermediate Marks Memo -> ACCEPT (Verified)")

    # 3.2 10th Marks Memo in Intermediate slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Intermediate Marks Memo",
        required_doc_type="intermediate_memo",
        file_path="tenth_memo.pdf",
        ocr_text=tenth_memo_text,
        opencv_quality=clear_quality,
        original_filename="10th_marks_memo.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    assert "Invalid Document Type" in r["reason"]
    print("PASS 3.2: 10th Marks Memo in Intermediate slot -> REJECT (Invalid Document Type)")

    # 3.3 Study and Conduct Certificate in Intermediate slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Intermediate Marks Memo",
        required_doc_type="intermediate_memo",
        file_path="study.pdf",
        ocr_text=tenth_study_text,
        opencv_quality=clear_quality,
        original_filename="study_and_conduct_certificate.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 3.3: 10th Study & Conduct in Intermediate slot -> REJECT (Invalid Document Type)")

    # 3.4 Intermediate Study & Conduct Certificate in Intermediate slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Intermediate Marks Memo",
        required_doc_type="intermediate_memo",
        file_path="inter_study.pdf",
        ocr_text=inter_study_text,
        opencv_quality=clear_quality,
        original_filename="intermediate_study_and_conduct_certificate.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 3.4: Intermediate Study & Conduct in Intermediate slot -> REJECT (Invalid Document Type)")

    # 3.5 PAN Card in Intermediate slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Intermediate Marks Memo",
        required_doc_type="intermediate_memo",
        file_path="pan.pdf",
        ocr_text=pan_text,
        opencv_quality=clear_quality,
        original_filename="pan_card.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 3.5: PAN Card in Intermediate slot -> REJECT (Invalid Document Type)")

    # 3.6 Aadhaar Card in Intermediate slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Intermediate Marks Memo",
        required_doc_type="intermediate_memo",
        file_path="aadhaar.pdf",
        ocr_text=aadhaar_text,
        opencv_quality=clear_quality,
        original_filename="aadhaar_card.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 3.6: Aadhaar Card in Intermediate slot -> REJECT (Invalid Document Type)")

    # 3.7 Income Certificate in Intermediate slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Intermediate Marks Memo",
        required_doc_type="intermediate_memo",
        file_path="income.pdf",
        ocr_text=income_text,
        opencv_quality=clear_quality,
        original_filename="income_certificate.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 3.7: Income Certificate in Intermediate slot -> REJECT (Invalid Document Type)")

    # 3.8 Any other document in Intermediate slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Intermediate Marks Memo",
        required_doc_type="intermediate_memo",
        file_path="other.pdf",
        ocr_text=other_text,
        opencv_quality=clear_quality,
        original_filename="other_doc.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}: {r['reason']}"
    print("PASS 3.8: Any other document in Intermediate slot -> REJECT (Invalid Document Type)")

    # 3.9 Blurry Intermediate Marks Memo -> POOR QUALITY
    r = GeminiVerificationService.verify_document(
        required_doc_name="Intermediate Marks Memo",
        required_doc_type="intermediate_memo",
        file_path="inter_memo_blurry.pdf",
        ocr_text=inter_memo_text,
        opencv_quality=blurry_quality,
        original_filename="inter_memo_blurry.pdf"
    )
    assert r["status"] == "poor_quality", f"Expected 'poor_quality', got {r['status']}: {r['reason']}"
    print("PASS 3.9: Blurry Intermediate Marks Memo -> POOR QUALITY (Correct Quality Issue Message)")

    # =========================================================================
    # PART 4: REGRESSION TESTS - PRESERVE ALL OTHER DOCUMENTS
    # =========================================================================
    print("\n--- PART 4: Regression Tests for Other Document Fields ---")

    # 4.1 Income Certificate in Income slot -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Income Certificate",
        required_doc_type="income_proof",
        file_path="income.pdf",
        ocr_text=income_text,
        opencv_quality=clear_quality,
        original_filename="income_certificate.pdf"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}"
    print("PASS 4.1: Income Certificate in Income slot -> ACCEPT (Verified)")

    # 4.2 Caste Certificate in Income slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Income Certificate",
        required_doc_type="income_proof",
        file_path="caste.pdf",
        ocr_text=caste_text,
        opencv_quality=clear_quality,
        original_filename="caste_certificate.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}"
    print("PASS 4.2: Caste Certificate in Income slot -> REJECT (Invalid Document Type)")

    # 4.3 10th Marks Memo in 10th Marks Memo slot -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="10th Marks Memo",
        required_doc_type="tenth_memo",
        file_path="tenth_memo.pdf",
        ocr_text=tenth_memo_text,
        opencv_quality=clear_quality,
        original_filename="10th_marks_memo.pdf"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}"
    print("PASS 4.3: 10th Marks Memo in 10th Marks Memo slot -> ACCEPT (Verified)")

    # 4.4 Intermediate Marks Memo in 10th Marks Memo slot -> REJECT
    r = GeminiVerificationService.verify_document(
        required_doc_name="10th Marks Memo",
        required_doc_type="tenth_memo",
        file_path="inter_memo.pdf",
        ocr_text=inter_memo_text,
        opencv_quality=clear_quality,
        original_filename="intermediate_marks_memo.pdf"
    )
    assert r["status"] == "invalid_type", f"Expected 'invalid_type', got {r['status']}"
    print("PASS 4.4: Intermediate Marks Memo in 10th Marks Memo slot -> REJECT (Invalid Document Type)")

    # 4.5 Caste Certificate in Caste slot -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Caste Certificate",
        required_doc_type="caste_proof",
        file_path="caste.pdf",
        ocr_text=caste_text,
        opencv_quality=clear_quality,
        original_filename="caste_certificate.pdf"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}"
    print("PASS 4.5: Caste Certificate in Caste slot -> ACCEPT (Verified)")

    # 4.6 Aadhaar Card in Aadhaar slot -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Aadhaar Card",
        required_doc_type="aadhaar_card",
        file_path="aadhaar.pdf",
        ocr_text=aadhaar_text,
        opencv_quality=clear_quality,
        original_filename="aadhaar_card.pdf"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}"
    print("PASS 4.6: Aadhaar Card in Aadhaar slot -> ACCEPT (Verified)")

    # 4.7 PAN Card in PAN slot -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="PAN Card",
        required_doc_type="pan_card",
        file_path="pan.pdf",
        ocr_text=pan_text,
        opencv_quality=clear_quality,
        original_filename="pan_card.pdf"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}"
    print("PASS 4.7: PAN Card in PAN slot -> ACCEPT (Verified)")

    # 4.8 Birth Certificate in Birth slot -> ACCEPT
    r = GeminiVerificationService.verify_document(
        required_doc_name="Birth Certificate",
        required_doc_type="birth_proof",
        file_path="birth.pdf",
        ocr_text=birth_text,
        opencv_quality=clear_quality,
        original_filename="birth_certificate.pdf"
    )
    assert r["status"] == "verified", f"Expected 'verified', got {r['status']}"
    print("PASS 4.8: Birth Certificate in Birth slot -> ACCEPT (Verified)")

    # Cleanup temporary test files
    for p in [valid_photo_path, blurry_photo_path, dark_photo_path]:
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass

    print("\n" + "=" * 75)
    print("ALL TESTS PASSED SUCCESSFULLY (100%)!")
    print("Exact 3 fields strictly enforced; all regression tests passed without regression.")
    print("=" * 75)

if __name__ == "__main__":
    run_all_tests()
