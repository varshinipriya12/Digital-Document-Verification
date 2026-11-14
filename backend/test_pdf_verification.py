import sys
import os
import pymupdf as fitz  # PyMuPDF

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from services.opencv_service import OpenCVQualityChecker
from services.ocr_service import OCRService
from services.gemini_service import GeminiVerificationService

def create_sample_pdf(filename: str, content_lines: list):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4
    text = "\n".join(content_lines)
    page.insert_text((50, 100), text, fontsize=14)
    path = os.path.join(os.path.dirname(__file__), filename)
    doc.save(path)
    doc.close()
    return path

def run_tests():
    print("==================================================")
    print("TESTING PDF CONTENT VERIFICATION (IGNORE FILENAME)")
    print("==================================================\n")

    # 1. Create PDFs with misleading/random filenames
    aadhaar_pdf = create_sample_pdf("random123.pdf", [
        "Government of India",
        "Unique Identification Authority of India",
        "Mera Aadhaar, Meri Pehchan",
        "Rahul Sharma",
        "DOB: 15/08/1995",
        "Male",
        "1234 5678 9012"
    ])

    pan_pdf = create_sample_pdf("test_doc.pdf", [
        "INCOME TAX DEPARTMENT",
        "GOVT. OF INDIA",
        "Permanent Account Number Card",
        "ABCDE1234F",
        "Name: RAHUL SHARMA",
        "Father's Name: SURESH SHARMA",
        "DOB: 15/08/1995"
    ])

    ration_pdf = create_sample_pdf("document.pdf", [
        "Department of Food & Civil Supplies",
        "Government of National Capital Territory",
        "Ration Card / Khadya Patrika",
        "Card No: RC/987654321",
        "Family Head: Suresh Sharma",
        "Category: APL / BPL"
    ])

    test_cases = [
        ("TEST A", "random123.pdf (Contains Aadhaar)", "Aadhaar Card", "aadhaar_card", aadhaar_pdf, ["needs_attention", "ready"]),
        ("TEST B", "random123.pdf (Contains Aadhaar)", "PAN Card", "pan_card", aadhaar_pdf, ["invalid"]),
        ("TEST C", "random123.pdf (Contains Aadhaar)", "Ration Card", "ration_card", aadhaar_pdf, ["invalid"]),
        ("TEST D", "test_doc.pdf (Contains PAN)", "Aadhaar Card", "aadhaar_card", pan_pdf, ["invalid"]),
        ("TEST E", "document.pdf (Contains Ration)", "Aadhaar Card", "aadhaar_card", ration_pdf, ["invalid"]),
        ("TEST F", "document.pdf (Contains Ration)", "Ration Card", "ration_card", ration_pdf, ["needs_attention", "ready"]),
    ]

    passed_count = 0
    for test_id, desc, req_name, req_type, pdf_path, allowed_statuses in test_cases:
        # Step 1: Render check
        img = OpenCVQualityChecker.load_image(pdf_path)
        q_res = OpenCVQualityChecker.analyze_quality(pdf_path)

        # Step 2: OCR check
        ocr_res = OCRService.extract_text(pdf_path)

        # Step 3: Verification check
        res = GeminiVerificationService.verify_document(
            required_doc_name=req_name,
            required_doc_description=f"Official {req_name}",
            expected_keywords=[],
            file_path=pdf_path,
            ocr_text=ocr_res.get("extracted_text", ""),
            opencv_quality=q_res,
            required_doc_type=req_type
        )

        status = res.get("status")
        detected_name = res.get("detected_name")
        reason = res.get("reason")

        is_pass = status in allowed_statuses
        if is_pass:
            passed_count += 1
            print(f"[{test_id}] {desc}")
            print(f"       Required: {req_name} | Detected: {detected_name} | Status: {status} [PASSED]")
            print(f"       Reason: {reason}\n")
        else:
            print(f"[{test_id}] {desc}")
            print(f"       Required: {req_name} | Detected: {detected_name} | Status: {status} [FAILED]")
            print(f"       Reason: {reason}\n")

    # Clean up test PDFs
    for p in [aadhaar_pdf, pan_pdf, ration_pdf]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    print(f"Summary: {passed_count}/{len(test_cases)} tests passed.")

if __name__ == "__main__":
    run_tests()
