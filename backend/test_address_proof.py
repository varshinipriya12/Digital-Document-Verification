import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.abspath("backend"))

from services.gemini_service import GeminiVerificationService

def test_address_proof_matching():
    allowed_docs = [
        {"type": "aadhaar_card", "name": "Aadhaar Card", "text": "Government of India Unique Identification Authority UIDAI 1234 5678 9012 Address: Hyderabad"},
        {"type": "voter_id", "name": "Voter ID Card", "text": "Election Commission of India Electoral Photo Identity Card EPIC WBG1234567 Address: Vijayawada"},
        {"type": "ration_card", "name": "Ration Card", "text": "State Civil Supplies Dept Ration Card Consumer Details Rice Card Family Address"},
        {"type": "house_tax_receipt", "name": "House Tax Receipt", "text": "Municipal Corporation Property Tax Assessment House Tax Receipt Door No 1-2-3 Address"},
        {"type": "telephone_bill", "name": "Telephone Bill", "text": "BSNL Bharat Sanchar Nigam Limited Telephone Bill Landline Subscriber Address Billing"},
        {"type": "electricity_bill", "name": "Electricity Bill", "text": "Electricity Bill Power Distribution Limited Consumer No 98765432 Service Address Premises"},
    ]

    dummy_quality = {"is_acceptable": True, "blur_score": 120.0, "issues": []}

    for doc in allowed_docs:
        print(f"Testing Address Proof upload with: {doc['name']}...")
        result = GeminiVerificationService._evaluate_type_match(
            expected_category="address_proof",
            required_doc_name="Address Proof",
            detected_type=doc["type"],
            detected_name=doc["name"],
            gemini_reason="Valid address document",
            gemini_confidence=95,
            opencv_quality=dummy_quality,
            ocr_text=doc["text"]
        )
        print(f" -> Status: {result.get('status')}, Result Code: {result.get('result_code')}, Reason: {result.get('reason')}")
        assert result.get("status") == "ready", f"Failed for {doc['name']}: {result}"

    # Test an INVALID document (e.g. PAN Card uploaded as Address Proof)
    print("\nTesting Address Proof with INVALID doc (PAN Card)...")
    invalid_result = GeminiVerificationService._evaluate_type_match(
        expected_category="address_proof",
        required_doc_name="Address Proof",
        detected_type="pan_card",
        detected_name="PAN Card",
        gemini_reason="Income Tax PAN",
        gemini_confidence=95,
        opencv_quality=dummy_quality,
        ocr_text="Income Tax Department Permanent Account Number ABCDE1234F"
    )
    print(f" -> Status: {invalid_result.get('status')}, Result Code: {invalid_result.get('result_code')}")
    assert invalid_result.get("status") == "invalid", f"Expected invalid for PAN card in Address Proof, got: {invalid_result}"

    print("\nTesting Heuristic Classifier for Address Proof slot...")
    for doc in allowed_docs:
        h_res = GeminiVerificationService._heuristic_classification(
            required_doc_name="Address Proof",
            expected_category="address_proof",
            expected_keywords=["address", "resident"],
            ocr_text=doc["text"],
            opencv_quality=dummy_quality,
            fallback_reason="Offline test",
            original_filename=f"{doc['type']}_sample.pdf"
        )
        print(f" -> Heuristic for {doc['name']}: Status={h_res.get('status')}, Detected={h_res.get('detected_name')}")
        assert h_res.get("status") == "ready", f"Heuristic failed for {doc['name']}: {h_res}"

    print("\n=== ALL ADDRESS PROOF ACCEPTANCE TESTS PASSED! ===")

if __name__ == "__main__":
    test_address_proof_matching()
