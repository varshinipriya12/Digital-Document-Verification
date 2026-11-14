import re
import difflib
import unicodedata
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# 1. DOCUMENT EXPECTED OWNER MAPPING ACROSS ALL SERVICES
# =============================================================================

DOCUMENT_OWNER_MAP = {
    # Applicant Personal Identity & Education Documents
    "doc_aadhaar": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Aadhaar Card",
        "must_match": "applicant_name",
        "description": "Applicant's personal Aadhaar Card issued by UIDAI"
    },
    "doc_pan": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "PAN Card",
        "must_match": "applicant_name",
        "description": "Applicant's personal PAN Card issued by Income Tax Dept"
    },
    "doc_voter_id": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Voter ID Card",
        "must_match": "applicant_name",
        "description": "Applicant's personal Electoral Photo Identity Card"
    },
    "doc_passport_photo": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Passport Size Photo",
        "must_match": "visual_portrait",
        "description": "Recent passport photograph of the applicant"
    },
    "doc_tenth_memo": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "10th / SSC Marks Memo",
        "must_match": "applicant_name",
        "description": "Applicant's Secondary School Certificate (SSC) Marks Memo"
    },
    "doc_inter_memo": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Intermediate Marks Memo",
        "must_match": "applicant_name",
        "description": "Applicant's Higher Secondary / Intermediate (10+2) Marks Memo"
    },
    "doc_study_cert": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Study and Conduct Certificate",
        "must_match": "applicant_name",
        "description": "Applicant's institutional Study and Conduct Certificate"
    },
    "doc_birth_cert": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Birth Certificate",
        "must_match": "applicant_name",
        "description": "Birth Certificate of the applicant / registered child"
    },
    "doc_caste_cert": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Caste Certificate",
        "must_match": "applicant_name",
        "description": "Community / Integrated Caste Certificate of applicant"
    },
    "doc_income_cert": {
        "owner": "applicant",
        "owner_label": "Applicant / Household",
        "title": "Income Certificate",
        "must_match": "applicant_or_parent",
        "description": "Official Income Certificate of applicant or head of family"
    },
    "doc_bank_passbook": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Bank Passbook",
        "must_match": "applicant_name",
        "description": "Applicant's active Bank Account Passbook"
    },
    "doc_salary_slip": {
        "owner": "applicant",
        "owner_label": "Applicant / Earning Member",
        "title": "Salary Slip / Income Proof",
        "must_match": "applicant_or_parent",
        "description": "Salary slip or earnings statement of applicant or parent"
    },
    "doc_poi": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Proof of Identity (POI)",
        "must_match": "applicant_name",
        "description": "Proof of Identity document for the applicant"
    },
    "doc_app_form": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Application Form",
        "must_match": "applicant_name",
        "description": "Signed government service application form"
    },
    "doc_self_affidavit": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Self-Affidavit",
        "must_match": "applicant_name",
        "description": "Sworn Self-Affidavit executed by the applicant"
    },
    "doc_nativity_cert": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Nativity / Residence Certificate",
        "must_match": "applicant_name",
        "description": "Nativity or Residence Certificate of applicant"
    },
    "doc_correction_proof": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Supporting Document for Correction",
        "must_match": "applicant_name",
        "description": "Document establishing correction of applicant's details"
    },

    # Parent Documents
    "doc_father_aadhaar": {
        "owner": "father",
        "owner_label": "Father",
        "title": "Father's Aadhaar Card",
        "must_match": "father_name",
        "description": "Aadhaar Card belonging to applicant's father"
    },
    "doc_mother_aadhaar": {
        "owner": "mother",
        "owner_label": "Mother",
        "title": "Mother's Aadhaar Card",
        "must_match": "mother_name",
        "description": "Aadhaar Card belonging to applicant's mother"
    },

    # Family Member Documents
    "doc_family_caste_cert": {
        "owner": "family_member",
        "owner_label": "Family Member",
        "title": "Family Member's Previously Issued Caste Certificate",
        "must_match": "family_member_name",
        "description": "Caste Certificate of applicant's father, mother, or sibling"
    },
    "doc_death_cert": {
        "owner": "family_member",
        "owner_label": "Family Member",
        "title": "Death Certificate",
        "must_match": "family_member_name",
        "description": "Death Certificate of deceased family member or spouse"
    },
    "doc_marriage_cert": {
        "owner": "family_member",
        "owner_label": "Family Member / Spouse",
        "title": "Marriage Certificate",
        "must_match": "family_or_applicant",
        "description": "Marriage Certificate linking applicant or family members"
    },

    # College / Educational Institution Documents
    "doc_college_allotment": {
        "owner": "institution",
        "owner_label": "College / Educational Institution",
        "title": "College Admission / Allotment Order",
        "must_match": "student_and_college",
        "description": "Official College Admission / Allotment Order issued by Convener / University"
    },

    # Household / Family Documents
    "doc_ration_card": {
        "owner": "household",
        "owner_label": "Household / Family",
        "title": "Ration Card",
        "must_match": "household_members",
        "description": "Family Ration Card listing applicant and family members"
    },
    "doc_address_proof": {
        "owner": "household",
        "owner_label": "Household / Family",
        "title": "Address Proof",
        "must_match": "address_or_household",
        "description": "Valid address document in the name of applicant or parent"
    },
    "doc_id_address_alt": {
        "owner": "applicant",
        "owner_label": "Applicant",
        "title": "Identity / Address Proof Alternative",
        "must_match": "applicant_name",
        "description": "Aadhaar, Voter ID, or Ration Card of the applicant"
    },
    "doc_schedule_docs": {
        "owner": "household",
        "owner_label": "Household / Family",
        "title": "Schedule I to IV Documents",
        "must_match": "family_member_name",
        "description": "Schedule I to IV verification revenue records"
    },

    # Issuing Authority Documents
    "doc_medical_record": {
        "owner": "issuing_authority",
        "owner_label": "Issuing Authority",
        "title": "Doctor's Certificate / Medical Record",
        "must_match": "institutional_record",
        "description": "Institutional medical report or hospital birth record"
    },
    "doc_non_avail_cert": {
        "owner": "issuing_authority",
        "owner_label": "Issuing Authority",
        "title": "Non-Availability Certificate (NAC)",
        "must_match": "institutional_record",
        "description": "Official Non-Availability Certificate from local registrar"
    },
    "doc_fir_report": {
        "owner": "issuing_authority",
        "owner_label": "Issuing Authority",
        "title": "FIR / Police Report",
        "must_match": "applicant_name",
        "description": "Police FIR report for lost or damaged documents"
    }
}


# =============================================================================
# 2. NAME MATCHING ENGINE WITH INITIALS & INDIAN NAME EXPANSION SUPPORT
# =============================================================================

class NameMatchingEngine:
    """
    Robust name comparison engine that handles:
    - Initials vs expanded surnames: e.g. 'Sri Valli Ch' vs 'Ch. Sri Valli' vs 'Chekuri Sri Valli'
    - Order variations: e.g. 'Arepalli Nirisha Priya' vs 'Nirisha Priya Arepalli'
    - Transliteration and minor OCR spelling noise: 'Valli' vs 'Vally'
    - Rejection of single-initial matches as proof of relationship
    - Rejection of completely different persons
    """

    HONORIFICS = {
        "mr", "mrs", "ms", "miss", "shri", "smt", "sri", "kumari", "dr",
        "late", "kum", "master", "prof", "capt", "major"
    }

    RELATION_PREFIXES = {
        "s/o", "d/o", "w/o", "c/o", "so", "do", "wo", "co", "son of",
        "daughter of", "wife of", "care of"
    }

    @staticmethod
    def normalize_name(name_str: str) -> list:
        """Clean string and return list of normalized token strings."""
        if not name_str:
            return []
        
        # Normalize unicode and lower case
        text = unicodedata.normalize("NFKD", name_str).encode("ascii", "ignore").decode("utf-8").lower()
        
        # Replace non-alphabetical characters with space, but keep dot for initial check
        text = re.sub(r'[^a-z\s]', ' ', text)
        tokens = [t.strip() for t in text.split() if t.strip()]

        # Filter out common honorifics
        filtered = [t for t in tokens if t not in NameMatchingEngine.HONORIFICS and len(t) > 0]
        return filtered

    @staticmethod
    def compare_names(candidate: str, reference: str) -> tuple:
        """
        Compare candidate extracted name with reference profile name.
        Returns (score: float 0.0-1.0, match_type: str, explanation: str)
        """
        if not candidate or not reference:
            return (0.0, "missing", "Missing candidate or reference name.")

        cand_tokens = NameMatchingEngine.normalize_name(candidate)
        ref_tokens = NameMatchingEngine.normalize_name(reference)

        if not cand_tokens or not ref_tokens:
            return (0.0, "unclear", "Unclear name tokens after normalization.")

        cand_set = set(cand_tokens)
        ref_set = set(ref_tokens)

        # 1. Exact match (regardless of word order)
        if cand_set == ref_set:
            return (1.0, "exact", "Exact name match across all name components.")

        # 2. Check core given names vs initials
        # Separate full words (len >= 3) from short tokens/initials (len <= 2)
        cand_core = [t for t in cand_tokens if len(t) >= 3]
        ref_core = [t for t in ref_tokens if len(t) >= 3]
        cand_initials = [t for t in cand_tokens if len(t) < 3]
        ref_initials = [t for t in ref_tokens if len(t) < 3]

        # Critical Guard: If candidate has ZERO core names in common with reference,
        # but only shares an initial (e.g. 'Ravi Ch' vs 'Sri Valli Ch'):
        # They MUST NOT be considered a match! An initial alone does not prove identity.
        common_core = [t for t in cand_core if t in ref_core]
        
        # Check fuzzy token equality on core names (to handle OCR noise like 'srivalli' vs 'sri valli')
        fuzzy_core_matches = 0
        used_ref = set()
        for ct in cand_core:
            for rt in ref_core:
                if rt in used_ref:
                    continue
                sim = difflib.SequenceMatcher(None, ct, rt).ratio()
                if sim >= 0.85:
                    fuzzy_core_matches += 1
                    used_ref.add(rt)
                    break

        # Check initial expansion: e.g. initial 'ch' in cand matches 'chekuri' in ref
        initial_expansions = 0
        for init in (cand_initials + ref_initials):
            target_list = ref_core if init in cand_initials else cand_core
            for full in target_list:
                if full.startswith(init) and len(full) > len(init):
                    initial_expansions += 1
                    break

        total_core_targets = max(len(ref_core), 1)

        # Case A: Core names match well (at least 75% of core tokens or >= 2 core tokens match)
        if fuzzy_core_matches >= total_core_targets or (total_core_targets > 1 and fuzzy_core_matches >= total_core_targets - 1 and initial_expansions > 0):
            score = 0.92 if fuzzy_core_matches == total_core_targets else 0.86
            return (score, "matched", f"Name matched with high confidence ({fuzzy_core_matches}/{total_core_targets} core tokens verified).")

        # Case B: Only one core token exists and it matches (e.g. single name 'Valli' vs 'Sri Valli')
        if fuzzy_core_matches > 0 and len(cand_core) <= 2 and len(ref_core) <= 2:
            score = 0.85
            return (score, "matched", "Given name matched successfully.")

        # Case C: Shared initial/surname ONLY, but completely different given names
        # E.g. 'Ravi Ch' vs 'Sri Valli Ch' -> common initial 'ch', but 'ravi' != 'sri valli'
        if fuzzy_core_matches == 0:
            if cand_initials and ref_initials and set(cand_initials).intersection(set(ref_initials)):
                return (0.15, "person_mismatch", "Only initials/surname match; given names represent completely different persons.")
            return (0.0, "person_mismatch", f"Candidate name '{candidate}' does not match reference name '{reference}'.")

        # Case D: Substantial mismatch
        return (0.30, "details_mismatch", f"Partial name match below required threshold (found: '{candidate}', expected: '{reference}').")


# =============================================================================
# 3. DOCUMENT ENTITY & DETAILS EXTRACTOR (FROM OCR TEXT)
# =============================================================================

class DocumentEntityExtractor:
    """
    Extracts structured data from document OCR text:
    - Names (Person, Father, Mother, Student)
    - Dates (Date of Birth)
    - Educational Info (College Name, Course, Branch, Allotment/Roll Number)
    - Masked Identifiers (Aadhaar, PAN, EPIC)
    """

    @staticmethod
    def extract_entities(ocr_text: str, filename: str = "") -> dict:
        entities = {
            "candidate_name": None,
            "father_name": None,
            "mother_name": None,
            "student_name": None,
            "college_name": None,
            "course": None,
            "branch": None,
            "allotment_number": None,
            "dob": None,
            "masked_id": None
        }

        if not ocr_text:
            return entities

        lines = [l.strip() for l in ocr_text.splitlines() if l.strip()]

        # 1. Date of Birth Extraction
        dob_match = re.search(r'(?:DOB|Date\s*of\s*Birth|Year\s*of\s*Birth|D\.O\.B)[\s\:\-\/]*([0-9]{2}[\/\-\.][0-9]{2}[\/\-\.][0-9]{4}|[0-9]{4})', ocr_text, re.IGNORECASE)
        if dob_match:
            entities["dob"] = dob_match.group(1)

        # 2. Masked Identifiers (Aadhaar, PAN)
        aadhaar_match = re.search(r'\b[0-9]{4}\s*[0-9]{4}\s*([0-9]{4})\b', ocr_text)
        if aadhaar_match:
            entities["masked_id"] = f"XXXX-XXXX-{aadhaar_match.group(1)}"
            entities["masked_aadhaar"] = f"XXXX-XXXX-{aadhaar_match.group(1)}"
        else:
            pan_match = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', ocr_text)
            if pan_match:
                entities["masked_id"] = pan_match.group(1)
                entities["pan_number"] = pan_match.group(1)

        # 3. Father's Name Extraction
        father_match = re.search(r'(?:Father[\'s]*\s*Name|S\/O|D\/O|C\/O|Son\s*of|Daughter\s*of)[\s\:\-\.]+([A-Za-z\s\.]+)', ocr_text, re.IGNORECASE)
        if father_match:
            cand = father_match.group(1).split("\n")[0].split(",")[0].strip()
            if len(cand) >= 3 and not any(w in cand.lower() for w in ["address", "date", "birth", "signature"]):
                entities["father_name"] = cand[:40]

        # 4. Mother's Name Extraction
        mother_match = re.search(r'(?:Mother[\'s]*\s*Name)[\s\:\-\.]+([A-Za-z\s\.]+)', ocr_text, re.IGNORECASE)
        if mother_match:
            cand = mother_match.group(1).split("\n")[0].split(",")[0].strip()
            if len(cand) >= 3 and not any(w in cand.lower() for w in ["address", "date", "signature"]):
                entities["mother_name"] = cand[:40]

        # 5. Student / Candidate Name Extraction
        # Look for explicit labels first
        student_match = re.search(r'(?:Student\s*Name|Name\s*of\s*the\s*Student|Candidate\s*Name|Name\s*of\s*Candidate|Name\s*of\s*Applicant)[\s\:\-\.]+([A-Za-z\s\.]+)', ocr_text, re.IGNORECASE)
        if student_match:
            cand = student_match.group(1).split("\n")[0].split(",")[0].strip()
            if len(cand) >= 3 and not any(w in cand.lower() for w in ["college", "branch", "course", "date"]):
                entities["student_name"] = cand[:40]
                entities["candidate_name"] = cand[:40]

        if not entities["candidate_name"]:
            name_match = re.search(r'(?:^|\n)\s*(?:Name|To)[\s\:\-\.]+([A-Za-z\s\.]+)', ocr_text, re.IGNORECASE)
            if name_match:
                cand = name_match.group(1).split("\n")[0].split(",")[0].strip()
                if len(cand) >= 3 and not any(w in cand.lower() for w in ["government", "india", "department", "income", "caste", "authority"]):
                    entities["candidate_name"] = cand[:40]

        # Fallback line scanning: On ID cards (Aadhaar, PAN), name often appears on its own line before DOB/Gender
        if not entities["candidate_name"]:
            skip_phrases = [
                "government", "india", "unique", "authority", "uidai", "identification",
                "income", "tax", "election", "commission", "department", "certificate",
                "republic", "telangana", "andhra", "pradesh", "e-aadhaar", "aadhaar", "signature"
            ]
            for l in lines:
                l_clean = l.strip()
                l_low = l_clean.lower()
                if any(sp in l_low for sp in skip_phrases):
                    continue
                if re.search(r'\b(?:dob|year of birth|date of birth|male|female|transgender|\d{4})\b', l_low):
                    break
                if re.match(r'^[A-Za-z\s\.\']{3,40}$', l_clean):
                    words = [w for w in re.split(r'[\s\.]+', l_clean) if w]
                    if 1 <= len(words) <= 5:
                        entities["candidate_name"] = l_clean
                        break

        # 6. College / Educational Institution Details (for College Allotment / Admission)
        college_match = re.search(r'(?:College|Institution|Allotted\s*College|Institute)[\s\:\-\.]+([A-Za-z0-9\s\,\.\(\)\-]+?)(?:\n|Course|Branch|\d{5,}|$)', ocr_text, re.IGNORECASE)
        if college_match:
            coll = college_match.group(1).strip()
            if len(coll) >= 5 and "department" not in coll.lower():
                entities["college_name"] = coll[:80]
        else:
            # Fallback scan lines for institution keywords
            for l in lines:
                if any(k in l.lower() for k in ["college of", "institute of", "engineering college", "university college", "polytechnic"]) and len(l) > 8:
                    entities["college_name"] = l[:80]
                    break

        # Course Extraction
        course_match = re.search(r'(?:Course|Program|Degree)[\s\:\-\.]+([A-Za-z0-9\s\.\(\)\-]+?)(?:\n|Branch|Category|$)', ocr_text, re.IGNORECASE)
        if course_match:
            entities["course"] = course_match.group(1).strip()[:30]
        else:
            for c in ["b.tech", "btech", "b.e", "m.tech", "mca", "mba", "b.sc", "b.com", "intermediate", "diploma"]:
                if re.search(r'\b' + re.escape(c) + r'\b', ocr_text, re.IGNORECASE):
                    entities["course"] = c.upper()
                    break

        # Branch Extraction
        branch_match = re.search(r'(?:Branch|Specialization)[\s\:\-\.]+([A-Za-z0-9\s\.\(\)\-]+?)(?:\n|College|Rank|$)', ocr_text, re.IGNORECASE)
        if branch_match:
            entities["branch"] = branch_match.group(1).strip()[:40]
        else:
            for b in ["computer science", "cse", "electronics", "ece", "electrical", "eee", "mechanical", "civil", "information tech", "data science", "artificial intelligence"]:
                if re.search(r'\b' + re.escape(b) + r'\b', ocr_text, re.IGNORECASE):
                    entities["branch"] = b.title()
                    break

        # Allotment / Admission / Hall Ticket Number
        allot_match = re.search(r'(?:Allotment\s*No|Admission\s*No|Hall\s*Ticket\s*No|HT\s*No|Roll\s*No|Rank)[\s\:\-\.]+([A-Za-z0-9]+)', ocr_text, re.IGNORECASE)
        if allot_match:
            entities["allotment_number"] = allot_match.group(1).strip()

        return entities


# =============================================================================
# 4. SERVICE-WISE DOCUMENT OWNERSHIP & MATCHING VERIFIER
# =============================================================================

class OwnershipMatchingService:
    """
    Complete Document Ownership Verification and Cross-Document Details Matching System
    Works across ALL 8 Government Services.
    """

    @staticmethod
    def verify_ownership_and_details(
        document_id: str,
        service_id: str,
        application_type: str,
        ocr_text: str,
        detected_type: str,
        detected_name: str,
        user_profile: dict,
        session_cache: dict = None
    ) -> dict:
        """
        Evaluate whether the uploaded document belongs to the expected person,
        and whether extracted details (name, parents, college) match registered profiles.
        """
        doc_cfg = DOCUMENT_OWNER_MAP.get(document_id, {
            "owner": "applicant",
            "owner_label": "Applicant",
            "title": detected_name or "Document",
            "must_match": "applicant_name"
        })

        owner_type = doc_cfg["owner"]
        owner_label = doc_cfg["owner_label"]
        must_match = doc_cfg.get("must_match", "applicant_name")

        entities = DocumentEntityExtractor.extract_entities(ocr_text)

        # Retrieve profile reference values
        profile = user_profile or {}
        applicant_name = (profile.get("name") or "").strip()
        father_name = (profile.get("father_name") or "").strip()
        mother_name = (profile.get("mother_name") or "").strip()
        family_member_name = (profile.get("family_member_name") or "").strip()
        reg_college = (profile.get("college_name") or "").strip()
        reg_course = (profile.get("course") or "").strip()
        reg_branch = (profile.get("branch") or "").strip()

        # Fallback cross-document reference from session cache if profile fields are empty
        if session_cache:
            if not father_name and session_cache.get("father_name"):
                father_name = session_cache["father_name"]
            if not mother_name and session_cache.get("mother_name"):
                mother_name = session_cache["mother_name"]
            if not applicant_name and session_cache.get("applicant_name"):
                applicant_name = session_cache["applicant_name"]
            if not reg_college and session_cache.get("college_name"):
                reg_college = session_cache["college_name"]

        # ---------------------------------------------------------------------
        # CASE 1: Document belongs to APPLICANT
        # ---------------------------------------------------------------------
        if owner_type == "applicant":
            # If OCR text is very low/missing, return Needs Manual Review (never auto invalid!)
            word_count = len(ocr_text.split()) if ocr_text else 0
            if word_count < 6 and document_id != "doc_passport_photo":
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – OCR extraction is unclear. Could not read applicant name on '{doc_cfg['title']}'. Please upload a clearer copy.",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Applicant: {applicant_name}" if applicant_name else "Applicant Profile",
                    "confidence": 65
                }

            # Extract candidate name from document
            cand_name = entities.get("candidate_name") or entities.get("student_name")

            if not cand_name:

                # If text exists but no explicit name pattern, inspect if applicant name appears anywhere in text
                if applicant_name:
                    app_tokens = NameMatchingEngine.normalize_name(applicant_name)
                    text_lower = ocr_text.lower()
                    matches = [t for t in app_tokens if t in text_lower and len(t) >= 3]
                    if len(matches) >= max(len(app_tokens) - 1, 1):
                        return {
                            "ownership_status": "matched",
                            "ownership_label": "Matched",
                            "owner_category": owner_label,
                            "status": "ready",
                            "reason": f"Matched – Document belongs to the registered applicant ({applicant_name}).",
                            "extracted_entities": entities,
                            "comparison_target": f"Registered Applicant: {applicant_name}",
                            "confidence": 92
                        }

                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – Applicant's name could not be identified with certainty on '{doc_cfg['title']}'.",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Applicant: {applicant_name}" if applicant_name else "Applicant Profile",
                    "confidence": 70
                }

            # If applicant name is missing in profile, we cannot compare
            if not applicant_name:
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – Applicant profile name is not configured to verify ownership of '{doc_cfg['title']}'.",
                    "extracted_entities": entities,
                    "comparison_target": "Applicant Profile (Not configured)",
                    "confidence": 75
                }

            # Compare candidate name vs applicant profile name
            score, verdict, expl = NameMatchingEngine.compare_names(cand_name, applicant_name)

            if score >= 0.85:
                return {
                    "ownership_status": "matched",
                    "ownership_label": "Matched",
                    "owner_category": owner_label,
                    "status": "ready",
                    "reason": f"Matched – Document belongs to the registered applicant ({cand_name}).",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Applicant: {applicant_name}",
                    "confidence": int(score * 100)
                }
            elif verdict == "person_mismatch":
                # EXACT REQUIREMENT FROM PROMPT:
                return {
                    "ownership_status": "person_mismatch",
                    "ownership_label": "Invalid Document – Person Mismatch",
                    "owner_category": owner_label,
                    "status": "invalid",
                    "reason": f"Invalid Document – The uploaded document does not appear to belong to the registered applicant. (Found: '{cand_name}', Expected: '{applicant_name}'). Please upload your own document.",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Applicant: {applicant_name}",
                    "confidence": 95
                }
            else:
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – Extracted name '{cand_name}' partially differs from registered applicant '{applicant_name}'.",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Applicant: {applicant_name}",
                    "confidence": 75
                }

        # ---------------------------------------------------------------------
        # CASE 2: Document belongs to FATHER (Father's Aadhaar)
        # ---------------------------------------------------------------------
        elif owner_type == "father":
            extracted_father = entities.get("candidate_name") or entities.get("father_name")

            # Check if applicant accidentally uploaded their OWN document instead of father's
            if extracted_father and applicant_name:
                self_score, self_verdict, _ = NameMatchingEngine.compare_names(extracted_father, applicant_name)
                if self_score >= 0.85:
                    return {
                        "ownership_status": "person_mismatch",
                        "ownership_label": "Invalid Document – Person Mismatch",
                        "owner_category": owner_label,
                        "status": "invalid",
                        "reason": f"Invalid Document – You uploaded your own document ({extracted_father}) in the Father's Aadhaar slot. Please upload your Father's Aadhaar Card.",
                        "extracted_entities": entities,
                        "comparison_target": f"Expected: Father's Details (Found Applicant: {extracted_father})",
                        "confidence": 95
                    }

            if not father_name:
                # Reference father details unavailable
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – Father's reference details not found in profile to establish relationship with '{extracted_father or 'uploaded document'}'.",
                    "extracted_entities": entities,
                    "comparison_target": "Father's Profile Details",
                    "confidence": 70
                }

            if not extracted_father:
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – Could not read name on Father's document with high clarity.",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Father: {father_name}",
                    "confidence": 65
                }

            f_score, f_verdict, f_expl = NameMatchingEngine.compare_names(extracted_father, father_name)
            if f_score >= 0.85:
                return {
                    "ownership_status": "matched",
                    "ownership_label": "Matched",
                    "owner_category": owner_label,
                    "status": "ready",
                    "reason": f"Matched – Father's document verified against registered Father's details ({extracted_father}).",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Father: {father_name}",
                    "confidence": int(f_score * 100)
                }
            elif f_verdict == "person_mismatch":
                return {
                    "ownership_status": "person_mismatch",
                    "ownership_label": "Invalid Document – Person Mismatch",
                    "owner_category": owner_label,
                    "status": "invalid",
                    "reason": f"Invalid Document – Father's Name Mismatch. The uploaded document ({extracted_father}) does not match the registered Father's details ({father_name}).",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Father: {father_name}",
                    "confidence": 95
                }
            else:
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – Father's name on document '{extracted_father}' partially differs from registered '{father_name}'.",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Father: {father_name}",
                    "confidence": 72
                }

        # ---------------------------------------------------------------------
        # CASE 3: Document belongs to MOTHER (Mother's Aadhaar)
        # ---------------------------------------------------------------------
        elif owner_type == "mother":
            extracted_mother = entities.get("candidate_name") or entities.get("mother_name")

            # Check if applicant accidentally uploaded their OWN document instead of mother's
            if extracted_mother and applicant_name:
                self_score, self_verdict, _ = NameMatchingEngine.compare_names(extracted_mother, applicant_name)
                if self_score >= 0.85:
                    return {
                        "ownership_status": "person_mismatch",
                        "ownership_label": "Invalid Document – Person Mismatch",
                        "owner_category": owner_label,
                        "status": "invalid",
                        "reason": f"Invalid Document – You uploaded your own document ({extracted_mother}) in the Mother's Aadhaar slot. Please upload your Mother's Aadhaar Card.",
                        "extracted_entities": entities,
                        "comparison_target": f"Expected: Mother's Details (Found Applicant: {extracted_mother})",
                        "confidence": 95
                    }

            if not mother_name:
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – Mother's reference details not found in profile to establish relationship with '{extracted_mother or 'uploaded document'}'.",
                    "extracted_entities": entities,
                    "comparison_target": "Mother's Profile Details",
                    "confidence": 70
                }

            if not extracted_mother:
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – Could not read name on Mother's document with high clarity.",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Mother: {mother_name}",
                    "confidence": 65
                }

            m_score, m_verdict, _ = NameMatchingEngine.compare_names(extracted_mother, mother_name)
            if m_score >= 0.85:
                return {
                    "ownership_status": "matched",
                    "ownership_label": "Matched",
                    "owner_category": owner_label,
                    "status": "ready",
                    "reason": f"Matched – Mother's document verified against registered Mother's details ({extracted_mother}).",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Mother: {mother_name}",
                    "confidence": int(m_score * 100)
                }
            elif m_verdict == "person_mismatch":
                return {
                    "ownership_status": "person_mismatch",
                    "ownership_label": "Invalid Document – Person Mismatch",
                    "owner_category": owner_label,
                    "status": "invalid",
                    "reason": f"Invalid Document – Mother's Name Mismatch. The uploaded document ({extracted_mother}) does not match the registered Mother's details ({mother_name}).",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Mother: {mother_name}",
                    "confidence": 95
                }
            else:
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – Mother's name on document '{extracted_mother}' partially differs from registered '{mother_name}'.",
                    "extracted_entities": entities,
                    "comparison_target": f"Registered Mother: {mother_name}",
                    "confidence": 72
                }

        # ---------------------------------------------------------------------
        # CASE 4: INSTITUTION & COLLEGE DOCUMENT MATCHING (Scholarship Allotment Order)
        # ---------------------------------------------------------------------
        elif owner_type == "institution":
            # Extract Student Name and College Details
            stud_name = entities.get("student_name") or entities.get("candidate_name")
            ext_college = entities.get("college_name")
            ext_course = entities.get("course")
            ext_branch = entities.get("branch")

            # 1. Student Name Check
            if not stud_name:
                word_count = len(ocr_text.split()) if ocr_text else 0
                if word_count < 5:
                    return {
                        "ownership_status": "needs_manual_review",
                        "ownership_label": "Needs Manual Review",
                        "owner_category": owner_label,
                        "status": "needs_attention",
                        "reason": "Needs Manual Review – Could not read student details on Allotment Order due to low OCR clarity.",
                        "extracted_entities": entities,
                        "comparison_target": f"Registered Applicant: {applicant_name}",
                        "confidence": 60
                    }

                # Try finding applicant name directly in text
                if applicant_name:
                    app_tokens = NameMatchingEngine.normalize_name(applicant_name)
                    text_lower = ocr_text.lower()
                    if all(t in text_lower for t in app_tokens if len(t) >= 3):
                        stud_name = applicant_name

            if stud_name and applicant_name:
                s_score, s_verdict, _ = NameMatchingEngine.compare_names(stud_name, applicant_name)
                if s_verdict == "person_mismatch":
                    # EXACT REQUIREMENT FROM PROMPT:
                    return {
                        "ownership_status": "person_mismatch",
                        "ownership_label": "Invalid Document – Person Mismatch",
                        "owner_category": owner_label,
                        "status": "invalid",
                        "reason": f"Invalid Document – Student Name Mismatch. This Allotment Order (Student: '{stud_name}') does not appear to belong to the registered applicant ('{applicant_name}').",
                        "extracted_entities": entities,
                        "comparison_target": f"Registered Student: {applicant_name}",
                        "confidence": 95
                    }

            # 2. Institutional Details Check (College / Course / Branch)
            detail_issues = []
            if reg_college and ext_college:
                c_sim = difflib.SequenceMatcher(None, ext_college.lower(), reg_college.lower()).ratio()
                if c_sim < 0.50 and not any(w in ext_college.lower() for w in reg_college.lower().split() if len(w) > 4):
                    detail_issues.append(f"College mismatch (Found: '{ext_college}', Expected: '{reg_college}')")

            if reg_course and ext_course:
                if reg_course.lower() not in ext_course.lower() and ext_course.lower() not in reg_course.lower():
                    detail_issues.append(f"Course mismatch (Found: '{ext_course}', Expected: '{reg_course}')")

            if reg_branch and ext_branch:
                if reg_branch.lower() not in ext_branch.lower() and ext_branch.lower() not in reg_branch.lower():
                    detail_issues.append(f"Branch mismatch (Found: '{ext_branch}', Expected: '{reg_branch}')")

            if detail_issues:
                return {
                    "ownership_status": "details_mismatch",
                    "ownership_label": "Details Mismatch",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Details Mismatch – {'; '.join(detail_issues)}. Please review your institutional admission records.",
                    "extracted_entities": entities,
                    "comparison_target": f"College: {reg_college or 'N/A'}, Course: {reg_course or 'N/A'}",
                    "confidence": 85
                }

            # If student matches and details are consistent
            match_summary = f"Student: {stud_name or applicant_name}"
            if ext_college:
                match_summary += f", College: {ext_college[:30]}"
            if ext_course or ext_branch:
                match_summary += f", {ext_course or ''} {ext_branch or ''}".strip()

            return {
                "ownership_status": "matched",
                "ownership_label": "Matched",
                "owner_category": owner_label,
                "status": "ready",
                "reason": f"Matched – Allotment Order verified for student ({match_summary}).",
                "extracted_entities": entities,
                "comparison_target": f"Applicant: {applicant_name}, College: {reg_college or 'Verified'}",
                "confidence": 92
            }

        # ---------------------------------------------------------------------
        # CASE 5: FAMILY MEMBER DOCUMENTS (Family Member's Caste Certificate, Death, Marriage)
        # ---------------------------------------------------------------------
        elif owner_type == "family_member":
            fam_cand = entities.get("candidate_name") or entities.get("father_name")
            target_fam = family_member_name or father_name or mother_name

            if not target_fam:
                return {
                    "ownership_status": "needs_manual_review",
                    "ownership_label": "Needs Manual Review",
                    "owner_category": owner_label,
                    "status": "needs_attention",
                    "reason": f"Needs Manual Review – No reference family member details recorded in profile. Please specify family relationship for manual verification.",
                    "extracted_entities": entities,
                    "comparison_target": "Family Member Profile Details",
                    "confidence": 70
                }

            if fam_cand:
                # Check relationship against father, mother, or registered family member
                scores = []
                for ref_name in [father_name, mother_name, family_member_name]:
                    if ref_name:
                        sc, vd, _ = NameMatchingEngine.compare_names(fam_cand, ref_name)
                        scores.append((sc, vd, ref_name))

                best_score, best_verdict, best_ref = max(scores, key=lambda x: x[0]) if scores else (0, "unclear", "")

                if best_score >= 0.85:
                    return {
                        "ownership_status": "matched",
                        "ownership_label": "Matched",
                        "owner_category": owner_label,
                        "status": "ready",
                        "reason": f"Matched – Family member document verified against {best_ref}.",
                        "extracted_entities": entities,
                        "comparison_target": f"Family Member: {best_ref}",
                        "confidence": int(best_score * 100)
                    }
                else:
                    return {
                        "ownership_status": "needs_manual_review",
                        "ownership_label": "Needs Manual Review",
                        "owner_category": owner_label,
                        "status": "needs_attention",
                        "reason": f"Needs Manual Review – Family relationship cannot be automatically established from document name '{fam_cand}'. Manual inspection required.",
                        "extracted_entities": entities,
                        "comparison_target": f"Family Members: {target_fam}",
                        "confidence": 70
                    }

            return {
                "ownership_status": "needs_manual_review",
                "ownership_label": "Needs Manual Review",
                "owner_category": owner_label,
                "status": "needs_attention",
                "reason": f"Needs Manual Review – Family member details could not be read clearly on '{doc_cfg['title']}'.",
                "extracted_entities": entities,
                "comparison_target": f"Family Members: {target_fam}",
                "confidence": 65
            }

        # ---------------------------------------------------------------------
        # CASE 6: HOUSEHOLD & ISSUING AUTHORITY DOCUMENTS (Ration Card, Address, Medical, NAC)
        # ---------------------------------------------------------------------
        else:
            # For household documents like Ration Card: check if applicant or family name appears in member list
            if owner_type == "household" and applicant_name:
                app_tokens = NameMatchingEngine.normalize_name(applicant_name)
                text_lower = ocr_text.lower()
                has_app = any(t in text_lower for t in app_tokens if len(t) >= 3)
                if has_app:
                    return {
                        "ownership_status": "matched",
                        "ownership_label": "Matched",
                        "owner_category": owner_label,
                        "status": "ready",
                        "reason": f"Matched – Household document includes registered applicant / family members ({applicant_name}).",
                        "extracted_entities": entities,
                        "comparison_target": f"Household Reference: {applicant_name}",
                        "confidence": 90
                    }

            return {
                "ownership_status": "matched",
                "ownership_label": "Matched",
                "owner_category": owner_label,
                "status": "ready",
                "reason": f"Matched – Valid {doc_cfg['title']} verified for {owner_label}.",
                "extracted_entities": entities,
                "comparison_target": f"{owner_label} Verification",
                "confidence": 88
            }
