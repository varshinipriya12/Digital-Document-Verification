import os
import re
import json
import logging
import numpy as np
from PIL import Image
import pymupdf as fitz
from config import Config
from services.opencv_service import OpenCVQualityChecker

logger = logging.getLogger(__name__)

# Try importing Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False
    logger.warning("google-genai SDK not installed or unavailable.")

class GeminiVerificationService:

    @staticmethod
    def verify_document(
        required_doc_name: str,
        required_doc_description: str = "",
        expected_keywords: list = None,
        file_path: str = "",
        ocr_text: str = "",
        opencv_quality: dict = None,
        required_doc_type: str = None,
        original_filename: str = ""
    ) -> dict:
        """
        Independent Document-Content Verification Pipeline:
        1. Render actual document page / image into RGB PIL Image.
        2. Gemini / Heuristic AI analyzes visual appearance + extracted text + filename signals to determine ACTUAL document type.
        3. Compare detected_type vs required expected_category.
        """
        api_key = Config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

        # Infer required document type tag
        expected_category = GeminiVerificationService._normalize_doc_type(required_doc_name, required_doc_type)

        # Render PDF/Image to BGR numpy array
        cv_img = OpenCVQualityChecker.load_image(file_path)
        if cv_img is None or cv_img.size == 0:
            if not ocr_text:
                return {
                    "status": "poor_quality",
                    "status_label": "Poor Quality",
                    "result_code": "⚠️ Poor Quality",
                    "detected_type": "other_unknown",
                    "detected_name": "Unreadable File",
                    "reason": "Document Quality Issue – Your uploaded document is blurry or unclear. Please upload a clear and readable document.",
                    "confidence": 0
                }
            # If OCR text exists, fall back to heuristic classification
            return GeminiVerificationService._heuristic_classification(
                required_doc_name=required_doc_name,
                expected_category=expected_category,
                expected_keywords=expected_keywords,
                ocr_text=ocr_text,
                opencv_quality=opencv_quality,
                fallback_reason="Image render unavailable, classified from OCR text.",
                original_filename=original_filename,
                file_path=file_path,
                cv_img=cv_img
            )

        # 1. Fallback to multi-signal heuristic classifier if Gemini API key missing or SDK unavailable
        if not api_key or not HAS_GENAI_SDK:
            reason_msg = "Gemini API key not configured." if not api_key else "GenAI SDK unavailable."
            return GeminiVerificationService._heuristic_classification(
                required_doc_name=required_doc_name,
                expected_category=expected_category,
                expected_keywords=expected_keywords,
                ocr_text=ocr_text,
                opencv_quality=opencv_quality,
                fallback_reason=reason_msg,
                original_filename=original_filename,
                file_path=file_path,
                cv_img=cv_img
            )

        # 2. Multimodal AI Verification using Gemini API on actual page image
        try:
            # Convert BGR OpenCV image to RGB PIL image for Gemini SDK
            rgb_img = cv2_bgr_to_rgb(cv_img)
            pil_image = Image.fromarray(rgb_img)

            prompt = f"""
You are an expert government document classification and verification assistant.

CRITICAL MANDATE:
Identify the ACTUAL DOCUMENT TYPE of the uploaded file based ON its visual layout, structure, logos, government emblems, text content, and visual format.

ALLOWED DETECTED DOCUMENT TYPES:
- "aadhaar_card": Aadhaar Card / e-Aadhaar issued by UIDAI / Govt of India (contains 12-digit UID format e.g. 1234 5678 9012, UIDAI logo, Govt of India emblem, Mera Aadhaar Meri Pehchan).
- "father_aadhaar": Father's Aadhaar Card (Aadhaar card belonging to applicant's father).
- "mother_aadhaar": Mother's Aadhaar Card (Aadhaar card belonging to applicant's mother).
- "pan_card": PAN Card / e-PAN issued by Income Tax Department / Govt of India (contains 10-char alphanumeric PAN format e.g. ABCDE1234F, Income Tax emblem, Father's Name).
- "voter_id": Voter ID / Electoral Photo Identity Card (EPIC) issued by Election Commission of India (contains EPIC number e.g. WBG1234567, ECI emblem, Electoral Officer).
- "caste_proof": Caste / Community / Tribe Certificate issued by Revenue Dept / Tahsildar.
- "income_proof": Tahsildar Income Certificate, Salary Slip, Form 16, Income Tax Return.
- "bank_passbook": First page of Bank Passbook showing Account No, IFSC, Branch stamp.
- "passport_photo": Passport size front-facing portrait photograph of a person (not an ID card or certificate).
- "ration_card": Ration Card / Smart Rice Card / Khadya Card issued by Food & Civil Supplies Dept.
- "tenth_study_conduct": 10th Class Study and Conduct Certificate / School Bonafide Certificate (NOT a marks memo).
- "intermediate_study_conduct": Intermediate Study and Conduct Certificate / Junior College Bonafide Certificate (NOT a marks memo).
- "study_certificate": Study and Conduct Certificate / Bonafide Certificate.
- "tenth_memo": 10th Class Marks Memo / SSC / Secondary School Certificate (subject-wise marks memo).
- "intermediate_memo": Intermediate Marks Memo / Higher Secondary (10+2) Marks Memorandum issued by Board of Intermediate Education.
- "birth_proof": Hospital Birth Certificate / Municipal Birth Registration Record.
- "college_allotment": College Admission / Seat Allotment Order / Admission Letter / Joining Report issued by Convener / University.
- "salary_slip": Income Proof / Salary Slip / Pay Slip / Form 16 showing monthly/annual earnings and employer details.
- "family_caste_proof": Family Member's (Father, Mother, Brother, Sister) Previously Issued Caste / Community Certificate.
- "house_tax_receipt": Address Proof - House Tax Receipt / Property Tax Assessment / Municipal Tax Paid Receipt.
- "telephone_bill": Address Proof - Telephone Bill / Landline / Broadband / Postpaid Mobile Utility Bill.
- "electricity_bill": Address Proof - Electricity Bill / Power Distribution Utility Bill / Discom Consumer Bill.
- "address_proof": Valid Address Proof (Ration Card, Voter ID, Aadhaar Card, House Tax Receipt, Telephone Bill, or Electricity Bill showing resident address).
- "identity_address_alt": Identity / Address proof (Aadhaar Card, Voter ID Card, or Ration Card).
- "proof_of_identity": Proof of Identity - POI (Aadhaar, PAN, Voter ID, Passport, or Govt ID).
- "application_form": Duly signed official service application form.
- "medical_record": Doctor's Certificate / Hospital Medical Record / Institutional Birth Report.
- "non_avail_cert": Non-Availability Certificate (NAC) from Gram Panchayat / Municipal Administration.
- "self_affidavit": Self-Affidavit on stamp paper.
- "death_proof": Death Certificate issued by Municipal / Panchayat Authority.
- "marriage_proof": Marriage Certificate / Registration Record.
- "schedule_docs": Schedule I to IV Documents / Revenue Inquiry Records.
- "fir_police_report": FIR / Police Complaint Report / Damaged EPIC replacement document.
- "nativity_cert": Nativity Certificate / Residence Certificate.
- "correction_proof": Supporting Document for Correction / Discrepancy Evidence.
- "other_unknown": Other unrecognized document, certificate, or paper.

EXTRACTED OCR TEXT FROM DOCUMENT PAGE:
\"\"\"{ocr_text[:1500]}\"\"\"

OPENCV QUALITY METRICS:
- Blur Score: {opencv_quality.get('blur_score')} (Scores < 80 indicate blurriness)
- Acceptable Quality: {opencv_quality.get('is_acceptable')}
- Quality Issues: {opencv_quality.get('issues')}

INSTRUCTIONS:
1. Examine the page image and text carefully. Determine `detected_type` and `detected_name`.
2. Compare `detected_type` against the required category "{expected_category}".
3. Respond strictly in valid JSON format:
{{
  "detected_type": "aadhaar_card" | "father_aadhaar" | "mother_aadhaar" | "pan_card" | "voter_id" | "caste_proof" | "income_proof" | "bank_passbook" | "passport_photo" | "ration_card" | "study_certificate" | "tenth_study_conduct" | "intermediate_study_conduct" | "tenth_memo" | "intermediate_memo" | "birth_proof" | "college_allotment" | "salary_slip" | "family_caste_proof" | "house_tax_receipt" | "telephone_bill" | "electricity_bill" | "address_proof" | "other_unknown",
  "detected_name": "Detected Human-Readable Document Name",
  "status": "ready" | "needs_attention" | "invalid",
  "reason": "Clear, detailed explanation of detected document type and verification result",
  "confidence": 95
}}
"""

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[pil_image, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )

            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            res_json = json.loads(response_text.strip())
            detected_type = res_json.get("detected_type", "other_unknown").lower()
            detected_name = res_json.get("detected_name", "Unknown Document")

            # Perform Backend Verification Logic on Gemini's Detected Type
            return GeminiVerificationService._evaluate_type_match(
                expected_category=expected_category,
                required_doc_name=required_doc_name,
                detected_type=detected_type,
                detected_name=detected_name,
                gemini_reason=res_json.get("reason"),
                gemini_confidence=res_json.get("confidence", 90),
                opencv_quality=opencv_quality,
                ocr_text=ocr_text
            )

        except Exception as e:
            logger.error(f"Gemini API verification exception: {str(e)}", exc_info=True)
            # Safe failure fallback - MUST NEVER auto-mark READY on API failure!
            return GeminiVerificationService._heuristic_classification(
                required_doc_name=required_doc_name,
                expected_category=expected_category,
                expected_keywords=expected_keywords,
                ocr_text=ocr_text,
                opencv_quality=opencv_quality,
                fallback_reason=f"Gemini API verification error ({str(e)}).",
                original_filename=original_filename,
                file_path=file_path
            )

    @staticmethod
    def _detect_actual_document_type(ocr_text: str = "", file_path: str = "", original_filename: str = "", cv_img: np.ndarray = None) -> tuple:
        """
        Analyze document content, structural patterns, and OCR text to determine
        the ACTUAL document type independently of the expected upload card.
        Does NOT rely on upload card labels.
        Returns: (detected_type: str, detected_name: str, confidence: int, is_uncertain: bool)
        """
        text = (ocr_text or "").lower()
        fn = (original_filename or os.path.basename(file_path or "")).lower()

        pan_regex = re.search(r'\b[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}\b', ocr_text or "")
        aadhaar_regex = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', ocr_text or "")
        voter_regex = re.search(r'\b[a-zA-Z]{3}\d{7}\b', ocr_text or "") or re.search(r'\b[a-zA-Z]{2,3}/\d{2,3}/\d{2,3}/\d{4,7}\b', ocr_text or "")

        # 1. PAN Card Detection
        if pan_regex or "permanent account number" in text or ("income tax department" in text and ("father" in text or "pan" in text or "signature" in text or "govt" in text)):
            return "pan_card", "PAN Card", 98, False

        # 2. Aadhaar Card Detection
        if ("uidai" in text or "unique identification" in text or "mera aadhaar" in text) or (aadhaar_regex and ("government of india" in text or "dob" in text or "enrolment" in text or "male" in text or "female" in text)):
            return "aadhaar_card", "Aadhaar Card", 98, False

        # 3. Voter ID Card Detection
        if voter_regex or "election commission" in text or "electoral photo identity" in text or "epic no" in text or "elector's name" in text or "e-electors" in text:
            return "voter_id", "Voter ID Card", 98, False

        # 4. Ration Card Detection
        if "ration card" in text or "rice card" in text or ("civil supplies" in text and "card" in text) or "ఆహార భద్రత" in text or "రేషన్ కార్డు" in text:
            return "ration_card", "Ration Card", 95, False

        # 5. Bank Passbook Detection
        if "passbook" in text or "pass book" in text or ("savings bank" in text and "account" in text) or (("account number" in text or "account no" in text or "a/c no" in text) and ("ifsc" in text or "branch" in text or "bank" in text)):
            return "bank_passbook", "Bank Passbook", 95, False

        # 6. Salary Slip Detection
        if "salary slip" in text or "payslip" in text or "pay slip" in text or ("basic pay" in text and ("net pay" in text or "gross salary" in text or "gross pay" in text or "hra" in text or "provident fund" in text or "pf deduction" in text)):
            return "salary_slip", "Salary Slip", 95, False

        # 7. Study and Conduct Certificate Detection (Checked BEFORE Marks Memos)
        is_study_conduct = (
            "study and conduct" in text or "study & conduct" in text or "bonafide certificate" in text or
            "bonafide student" in text or
            ("conduct certificate" in text and any(w in text for w in ["pupil", "student", "academic year", "institution", "school", "college", "conduct", "character"])) or
            ("study certificate" in text and any(w in text for w in ["pupil", "student", "academic year", "institution", "school", "college", "conduct", "character"]))
        )
        if is_study_conduct:
            if any(k in text for k in ["intermediate", "inter 1st", "inter 2nd", "junior college", "+2", "10+2", "higher secondary", "mpc", "bipc", "cec", "hec"]):
                return "intermediate_study_conduct", "Intermediate Study and Conduct Certificate", 96, False
            else:
                return "tenth_study_conduct", "10th Study and Conduct Certificate", 96, False

        # 8. Intermediate Marks Memo Detection
        is_inter_memo = (
            ("board of intermediate education" in text or "intermediate public examination" in text or "intermediate education" in text or "senior school certificate examination" in text or (("intermediate" in text or "junior college" in text or "+2" in text or "10+2" in text) and any(m in text for m in ["marks", "memorandum", "grade", "total marks", "pass certificate", "gpa", "memo"])))
            and any(k in text for k in ["marks", "grade", "points", "memorandum", "pass certificate", "total marks", "gpa", "memo"])
            and not any(k in text for k in ["secondary school certificate", "board of secondary education", "10th class", "class x", "ssc marks", "ssc public"])
        )
        if is_inter_memo:
            return "intermediate_memo", "Intermediate Marks Memo", 96, False

        # 9. 10th Marks Memo Detection
        is_tenth_memo = (
            ("secondary school certificate" in text or "board of secondary education" in text or "ssc" in text or "10th class" in text or "class x" in text or "tenth class" in text or "secondary school examination" in text)
            and any(m in text for m in ["marks", "gpa", "grade", "points", "hall ticket", "roll no", "memorandum", "memo"])
            and not any(k in text for k in ["board of intermediate education", "intermediate public examination", "junior college"])
        )
        if is_tenth_memo:
            return "tenth_memo", "10th Marks Memo", 96, False

        # 10. College Admission / Allotment Order Detection
        if "allotment order" in text or "seat allotment" in text or ("convener" in text and "admission" in text) or ("joining report" in text and "college" in text):
            return "college_allotment", "College Admission / Allotment Order", 95, False

        # 11. Caste Certificate Detection (Prioritized before birth/generic checks)
        has_caste_title = any(k in text for k in ["caste certificate", "community certificate", "integrated community certificate", "community, nativity", "caste and community", "caste claim", "కుల ధ్రువీకరణ", "కుల ధృవీకరణ", "జాతి ధ్రువీకరణ"])
        has_caste_body = any(k in text for k in ["backward class", "scheduled caste", "scheduled tribe", "belongs to", "caste which is recognized", "sub-caste"]) and any(k in text for k in ["revenue department", "tahsildar", "mandal", "certify", "g.o.ms"])
        if has_caste_title or has_caste_body:
            return "caste_proof", "Caste Certificate", 96, False

        # 12. Birth Certificate Detection (Exclusively true birth certificates)
        has_birth_title = any(k in text for k in ["birth certificate", "certificate of birth", "registrar of births and deaths", "form no. 5", "form 5", "జనన ధ్రువీకరణ", "జనన ధృవీకరణ"])
        has_birth_body = ("place of birth" in text or "name of child" in text or "child name" in text) and ("date of birth" in text or "born on" in text)
        if has_birth_title or has_birth_body:
            return "birth_proof", "Birth Certificate", 95, False

        # 13. Income Certificate Detection (Disambiguated from Caste, Birth, Salary, PAN)
        has_income_cert_title = "income certificate" in text or "certificate of income" in text or "ఆదాయ ధ్రువీకరణ" in text or "ఆదాయ ధృవీకరణ" in text or "ఆదాయం" in text
        has_income_phrase = "annual income from all sources" in text or "income from all sources" in text or "annual income" in text or "gross annual income" in text or "total annual income" in text or "income of the family" in text or (("income is rs" in text or "annual income of rs" in text or "income of rs." in text or "/ - per annum" in text or "/= per annum" in text or "per annum" in text) and ("income" in text or "tahsildar" in text or "revenue department" in text))
        if has_income_cert_title or has_income_phrase:
            return "income_proof", "Income Certificate", 96, False

        # 14. Passport Size Photo Detection (Image-based classification)
        is_photo, photo_reason, photo_conf = OpenCVQualityChecker.classify_passport_photo(
            file_path=file_path,
            cv_img=cv_img,
            ocr_text=ocr_text,
            filename=original_filename or fn
        )
        if is_photo:
            return "passport_photo", "Passport Size Photo", photo_conf, False

        # 15. Additional Utility Document Categories
        if "house tax" in text or "property tax" in text or "assessment no" in text:
            return "house_tax_receipt", "House Tax Receipt", 95, False
        if "telephone bill" in text or "phone bill" in text or "broadband" in text or "landline" in text:
            return "telephone_bill", "Telephone Bill", 95, False
        if "electricity bill" in text or "power distribution" in text or "consumer no" in text or "discom" in text:
            return "electricity_bill", "Electricity Bill", 95, False
        if "passport" in text and "republic of india" in text:
            return "passport", "Passport", 95, False

        # 16. OCR text has readable words but did not match any known document type -> other_unknown
        words = [w for w in text.split() if len(w) > 1]
        if len(words) >= 4:
            return "other_unknown", "Unrelated Document", 50, False

        # 17. Fallback for image scans without OCR engine available:
        # Check filename signals as a secondary cue only if OCR text is empty
        if any(k in fn for k in ["photo", "passport", "pic", "portrait"]) and not any(k in fn for k in ["pan", "aadhaar", "caste", "income"]):
            return "passport_photo", "Passport Size Photo", 80, False
        if any(k in fn for k in ["study", "conduct", "bonafide"]):
            if any(k in fn for k in ["inter", "+2", "college"]):
                return "intermediate_study_conduct", "Intermediate Study and Conduct Certificate", 80, False
            else:
                return "tenth_study_conduct", "10th Study and Conduct Certificate", 80, False
        if any(k in fn for k in ["intermediate", "inter", "12th", "+2"]) and any(k in fn for k in ["marks", "memo", "marksheet"]):
            return "intermediate_memo", "Intermediate Marks Memo", 80, False
        if any(k in fn for k in ["10th", "tenth", "ssc"]) and any(k in fn for k in ["marks", "memo", "marksheet"]):
            return "tenth_memo", "10th Marks Memo", 80, False
        if any(k in fn for k in ["income", "aadhayam", "aadaayam"]):
            return "income_proof", "Income Certificate", 80, False
        if any(k in fn for k in ["caste", "community"]):
            return "caste_proof", "Caste Certificate", 80, False
        if any(k in fn for k in ["birth", "janan"]):
            return "birth_proof", "Birth Certificate", 80, False
        if any(k in fn for k in ["pan", "pancard"]):
            return "pan_card", "PAN Card", 80, False
        if any(k in fn for k in ["aadhaar", "adhar", "uidai"]):
            return "aadhaar_card", "Aadhaar Card", 80, False
        if any(k in fn for k in ["vote", "voter", "epic"]):
            return "voter_id", "Voter ID Card", 80, False
        if any(k in fn for k in ["passbook", "bank"]):
            return "bank_passbook", "Bank Passbook", 80, False
        if any(k in fn for k in ["ration", "khadya", "ricecard"]):
            return "ration_card", "Ration Card", 80, False
        if any(k in fn for k in ["salary", "payslip", "pay_slip"]):
            return "salary_slip", "Salary Slip", 80, False

        # Truly uncertain / unidentifiable
        return "uncertain", "Uncertain Document Type", 40, True

    @staticmethod
    def _evaluate_type_match(
        expected_category: str,
        required_doc_name: str,
        detected_type: str,
        detected_name: str,
        gemini_reason: str,
        gemini_confidence: int,
        opencv_quality: dict,
        ocr_text: str = "",
        is_uncertain: bool = False
    ) -> dict:
        """
        Enforce strict type matching and clarity validation:
        - If classification is uncertain -> NEEDS REVIEW (never auto-accept)
        - If detected_type is unrelated/unknown or != expected -> INVALID DOCUMENT TYPE
        - If detected_type == expected and clear -> VERIFIED
        - If detected_type == expected but blurry -> POOR QUALITY
        """
        # 1. Uncertain classification -> NEEDS REVIEW
        if is_uncertain or detected_type == "uncertain":
            return {
                "status": "needs_review",
                "status_label": "Needs Review",
                "result_code": "⚠️ Needs Review",
                "detected_type": "uncertain",
                "detected_name": detected_name or "Uncertain Document Type",
                "reason": "Needs Review – AI/OCR cannot confidently identify the document type. Please upload a clear document.",
                "confidence": int(gemini_confidence or 50)
            }

        # 2. Unidentified / unrelated document -> INVALID DOCUMENT TYPE
        if detected_type == "other_unknown" or not detected_type:
            return {
                "status": "invalid_type",
                "status_label": "Invalid Document Type",
                "result_code": "❌ Invalid Document Type",
                "detected_type": "other_unknown",
                "detected_name": "Unrelated Document",
                "reason": "Invalid Document Type – The uploaded file does not match the selected document. Please upload the correct document.",
                "confidence": int(gemini_confidence or 50)
            }

        # 3. Compare detected_type against expected_category
        # STRICT MATCHING:
        # Income Certificate field MUST ONLY accept Income Certificate!
        is_type_match = False
        if expected_category == "income_proof":
            is_type_match = (detected_type == "income_proof")
        elif expected_category == "passport_photo":
            is_type_match = (detected_type == "passport_photo")
        elif expected_category == "study_certificate":
            is_type_match = (detected_type in ["tenth_study_conduct", "intermediate_study_conduct", "study_certificate"])
        elif expected_category == "intermediate_memo":
            is_type_match = (detected_type == "intermediate_memo")
        elif expected_category == "tenth_memo":
            is_type_match = (detected_type == "tenth_memo")
        elif expected_category == "caste_proof":
            is_type_match = (detected_type in ["caste_proof", "family_caste_proof"])
        elif expected_category == "family_caste_proof":
            is_type_match = (detected_type in ["family_caste_proof", "caste_proof"])
        elif expected_category == "birth_proof":
            is_type_match = (detected_type == "birth_proof")
        elif expected_category == "pan_card":
            is_type_match = (detected_type == "pan_card")
        elif expected_category in ["father_aadhaar", "mother_aadhaar", "aadhaar_card"]:
            is_type_match = (detected_type in ["father_aadhaar", "mother_aadhaar", "aadhaar_card"])
        elif expected_category == "voter_id":
            is_type_match = (detected_type == "voter_id")
        elif expected_category == "ration_card":
            is_type_match = (detected_type == "ration_card")
        elif expected_category == "bank_passbook":
            is_type_match = (detected_type == "bank_passbook")
        elif expected_category == "salary_slip":
            is_type_match = (detected_type in ["salary_slip", "income_proof"])
        elif expected_category == "college_allotment":
            is_type_match = (detected_type in ["college_allotment", "study_certificate", "tenth_study_conduct", "intermediate_study_conduct"])
        elif expected_category == detected_type:
            is_type_match = True
        elif expected_category == "address_proof" and detected_type in [
            "address_proof", "aadhaar_card", "voter_id", "ration_card",
            "house_tax_receipt", "telephone_bill", "electricity_bill"
        ]:
            is_type_match = True
        elif expected_category in ["house_tax_receipt", "telephone_bill", "electricity_bill"] and detected_type in [expected_category, "address_proof"]:
            is_type_match = True
        elif expected_category == "identity_address_alt" and detected_type in [
            "identity_address_alt", "aadhaar_card", "father_aadhaar", "mother_aadhaar", "voter_id", "ration_card", "address_proof"
        ]:
            is_type_match = True
        elif expected_category == "proof_of_identity" and detected_type in [
            "proof_of_identity", "aadhaar_card", "pan_card", "voter_id", "passport_photo"
        ]:
            is_type_match = True
        elif expected_category == "application_form" and detected_type in ["application_form"]:
            is_type_match = True
        elif expected_category == "medical_record" and detected_type in ["medical_record", "birth_proof"]:
            is_type_match = True
        elif expected_category == "non_avail_cert" and detected_type in ["non_avail_cert", "birth_proof"]:
            is_type_match = True
        elif expected_category == "self_affidavit" and detected_type in ["self_affidavit"]:
            is_type_match = True
        elif expected_category == "death_proof" and detected_type in ["death_proof"]:
            is_type_match = True
        elif expected_category == "marriage_proof" and detected_type in ["marriage_proof"]:
            is_type_match = True
        elif expected_category == "schedule_docs" and detected_type in ["schedule_docs", "caste_proof", "family_caste_proof"]:
            is_type_match = True
        elif expected_category == "fir_police_report" and detected_type in ["fir_police_report", "voter_id"]:
            is_type_match = True
        elif expected_category == "nativity_cert" and detected_type in ["nativity_cert", "caste_proof", "address_proof"]:
            is_type_match = True
        elif expected_category == "correction_proof" and detected_type not in ["other_unknown"]:
            is_type_match = True

        # 4. Wrong document -> INVALID DOCUMENT TYPE
        if not is_type_match:
            return {
                "status": "invalid_type",
                "status_label": "Invalid Document Type",
                "result_code": "❌ Invalid Document Type",
                "detected_type": detected_type,
                "detected_name": detected_name,
                "reason": "Invalid Document Type – The uploaded file does not match the selected document. Please upload the correct document.",
                "confidence": int(gemini_confidence or 95)
            }

        # 5. Document Quality & Clarity Check (OpenCV & Readability)
        is_blurry = not opencv_quality.get("is_acceptable", True)
        is_unreadable = False
        if ocr_text and ocr_text.strip():
            words = [w for w in ocr_text.split() if len(w) > 1]
            if len(words) < 5 and expected_category != "passport_photo":
                is_unreadable = True
        elif opencv_quality.get("contrast_std", 50.0) < 15.0:
            is_unreadable = True

        if is_blurry or is_unreadable:
            return {
                "status": "poor_quality",
                "status_label": "Poor Quality",
                "result_code": "⚠️ Poor Quality",
                "detected_type": detected_type,
                "detected_name": detected_name,
                "reason": "Document Quality Issue – Your uploaded document is blurry or unclear. Please upload a clear and readable document.",
                "confidence": int(gemini_confidence or 80)
            }

        # 6. Correct document type and acceptable quality -> VERIFIED
        return {
            "status": "verified",
            "status_label": "Verified",
            "result_code": "✅ Verified",
            "detected_type": detected_type,
            "detected_name": detected_name,
            "reason": "Verified – Document matches the required document type and quality is acceptable.",
            "confidence": int(gemini_confidence or 95)
        }

    @staticmethod
    def _heuristic_classification(
        required_doc_name: str,
        expected_category: str,
        expected_keywords: list,
        ocr_text: str,
        opencv_quality: dict,
        fallback_reason: str,
        original_filename: str = "",
        file_path: str = "",
        cv_img: np.ndarray = None
    ) -> dict:
        """
        Classify document using actual document content and evaluate type match against
        the expected category configured for the selected upload card.
        """
        detected_type, detected_name, confidence, is_uncertain = GeminiVerificationService._detect_actual_document_type(
            ocr_text=ocr_text,
            file_path=file_path,
            original_filename=original_filename,
            cv_img=cv_img
        )

        return GeminiVerificationService._evaluate_type_match(
            expected_category=expected_category,
            required_doc_name=required_doc_name,
            detected_type=detected_type,
            detected_name=detected_name,
            gemini_reason=fallback_reason,
            gemini_confidence=confidence,
            opencv_quality=opencv_quality,
            ocr_text=ocr_text,
            is_uncertain=is_uncertain
        )

    @staticmethod
    def _normalize_doc_type(name: str, doc_type: str = None) -> str:
        """Map document name or slug to normalized document category tag."""
        if doc_type:
            dt = doc_type.lower()
            if dt in ["aadhaar_card", "pan_card", "voter_id", "caste_proof", "income_proof",
                      "bank_passbook", "passport_photo", "ration_card", "study_certificate",
                      "tenth_memo", "intermediate_memo", "father_aadhaar", "mother_aadhaar", "birth_proof",
                      "college_allotment", "salary_slip", "family_caste_proof",
                      "house_tax_receipt", "telephone_bill", "electricity_bill", "address_proof",
                      "identity_address_alt", "proof_of_identity", "application_form", "medical_record",
                      "non_avail_cert", "self_affidavit", "death_proof", "marriage_proof",
                      "schedule_docs", "fir_police_report", "nativity_cert", "correction_proof"]:
                return dt
        name_lower = name.lower()
        if "or voter id card or ration card" in name_lower or "identity-address" in name_lower or "identity_address_alt" in name_lower:
            return "identity_address_alt"
        if "proof of identity" in name_lower or "poi" in name_lower:
            return "proof_of_identity"
        if "application form" in name_lower:
            return "application_form"
        if "medical" in name_lower or "doctor" in name_lower:
            return "medical_record"
        if "non-availability" in name_lower or "non availability" in name_lower or "nac" in name_lower:
            return "non_avail_cert"
        if "affidavit" in name_lower:
            return "self_affidavit"
        if "death" in name_lower:
            return "death_proof"
        if "marriage" in name_lower:
            return "marriage_proof"
        if "schedule" in name_lower:
            return "schedule_docs"
        if "fir" in name_lower or "police report" in name_lower:
            return "fir_police_report"
        if "nativity" in name_lower:
            return "nativity_cert"
        if "correction" in name_lower or "supporting document" in name_lower:
            return "correction_proof"
        if "address" in name_lower:
            return "address_proof"
        if "father" in name_lower and "aadhaar" in name_lower:
            return "father_aadhaar"
        if "mother" in name_lower and "aadhaar" in name_lower:
            return "mother_aadhaar"
        if "allotment" in name_lower or "admission" in name_lower:
            return "college_allotment"
        if "salary" in name_lower or "payslip" in name_lower or "pay slip" in name_lower:
            return "salary_slip"
        if "family" in name_lower and ("caste" in name_lower or "community" in name_lower):
            return "family_caste_proof"
        if "house tax" in name_lower or "property tax" in name_lower:
            return "house_tax_receipt"
        if "telephone" in name_lower or "phone bill" in name_lower:
            return "telephone_bill"
        if "electricity" in name_lower or "electric" in name_lower:
            return "electricity_bill"
        if "aadhaar" in name_lower:
            return "aadhaar_card"
        if "pan" in name_lower:
            return "pan_card"
        if "voter" in name_lower or "epic" in name_lower:
            return "voter_id"
        if "caste" in name_lower or "community" in name_lower:
            return "caste_proof"
        if "income" in name_lower:
            return "income_proof"
        if "passbook" in name_lower or "bank" in name_lower:
            return "bank_passbook"
        if "photo" in name_lower:
            return "passport_photo"
        if "ration" in name_lower:
            return "ration_card"
        if "study" in name_lower or "bonafide" in name_lower or "conduct" in name_lower:
            return "study_certificate"
        if "10th" in name_lower or "tenth" in name_lower or "ssc" in name_lower:
            return "tenth_memo"
        if "inter" in name_lower or "intermediate" in name_lower or "12th" in name_lower or "+2" in name_lower:
            return "intermediate_memo"
        if "birth" in name_lower:
            return "birth_proof"
        return "other_unknown"

def cv2_bgr_to_rgb(img: np.ndarray) -> np.ndarray:
    """Convert OpenCV BGR image to RGB numpy array."""
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
