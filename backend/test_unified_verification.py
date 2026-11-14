import sys
import os
import io

# Ensure utf-8 stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath("backend"))

from app import app
from database.mongodb import get_users_collection, get_verification_sessions_collection
from services.auth_service import AuthService

def test_full_unified_flow():
    client = app.test_client()

    print("=== TEST 1: Check Services API ===")
    res = client.get("/api/services")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.get_json()
    services = data.get("services", [])
    print(f"Services returned: {len(services)}")
    assert len(services) >= 8, f"Expected at least 8 services, got {len(services)}"
    service_slugs = [s.get("slug") for s in services]
    for required_slug in [
        "income-certificate", "caste-certificate", "birth-certificate",
        "aadhaar-card", "pan-card", "voter-id-card", "scholarship-application",
        "ration-card"
    ]:
        assert required_slug in service_slugs, f"Missing required service slug: {required_slug}"
    print("All 8 official government services returned by API!")

    print("\n=== TEST 2: Check Service-Wise Independent Document Checklists ===")

    # 2.1 Income Certificate (New: 3 docs, Update: 3 docs)
    res_inc_new = client.get("/api/services/income-certificate/documents?type=new")
    assert res_inc_new.status_code == 200
    inc_new_docs = res_inc_new.get_json().get("documents", [])
    print(f"Income Certificate (New Application) docs: {len(inc_new_docs)}")
    assert len(inc_new_docs) == 3, f"Expected 3 docs for Income Certificate New, got {len(inc_new_docs)}"
    assert "doc_id_address_alt" in [d["document_id"] for d in inc_new_docs]
    assert "doc_salary_slip" in [d["document_id"] for d in inc_new_docs]
    assert "doc_app_form" in [d["document_id"] for d in inc_new_docs]

    res_inc_upd = client.get("/api/services/income-certificate/documents?type=update")
    assert res_inc_upd.status_code == 200
    inc_upd_docs = res_inc_upd.get_json().get("documents", [])
    print(f"Income Certificate (Update) docs: {len(inc_upd_docs)}")
    assert len(inc_upd_docs) == 3, f"Expected 3 docs for Income Certificate Update, got {len(inc_upd_docs)}"
    assert "doc_income_cert" in [d["document_id"] for d in inc_upd_docs]
    assert "doc_aadhaar" in [d["document_id"] for d in inc_upd_docs]
    assert "doc_correction_proof" in [d["document_id"] for d in inc_upd_docs]

    # 2.2 Caste Certificate (New: 6 docs, Update: 4 docs)
    res_caste_new = client.get("/api/services/caste-certificate/documents?type=new")
    assert res_caste_new.status_code == 200
    caste_new_docs = res_caste_new.get_json().get("documents", [])
    print(f"Caste Certificate (New Application) docs: {len(caste_new_docs)}")
    assert len(caste_new_docs) == 6, f"Expected 6 docs for Caste Certificate New, got {len(caste_new_docs)}"

    res_caste_upd = client.get("/api/services/caste-certificate/documents?type=update")
    assert res_caste_upd.status_code == 200
    caste_upd_docs = res_caste_upd.get_json().get("documents", [])
    print(f"Caste Certificate (Update) docs: {len(caste_upd_docs)}")
    assert len(caste_upd_docs) == 4, f"Expected 4 docs for Caste Certificate Update, got {len(caste_upd_docs)}"

    # 2.3 Birth Certificate (New Normal: 2 docs, New Late: 5 docs, Update: 4 docs)
    res_birth_norm = client.get("/api/services/birth-certificate/documents?type=new&sub_operation=normal")
    assert res_birth_norm.status_code == 200
    birth_norm_docs = res_birth_norm.get_json().get("documents", [])
    print(f"Birth Certificate (Normal Registration) docs: {len(birth_norm_docs)}")
    assert len(birth_norm_docs) == 2, f"Expected 2 docs for Normal Birth, got {len(birth_norm_docs)}"

    res_birth_late = client.get("/api/services/birth-certificate/documents?type=new&sub_operation=late")
    assert res_birth_late.status_code == 200
    birth_late_docs = res_birth_late.get_json().get("documents", [])
    print(f"Birth Certificate (Late Registration) docs: {len(birth_late_docs)}")
    assert len(birth_late_docs) == 5, f"Expected 5 docs for Late Birth, got {len(birth_late_docs)}"

    res_birth_upd = client.get("/api/services/birth-certificate/documents?type=update")
    assert res_birth_upd.status_code == 200
    birth_upd_docs = res_birth_upd.get_json().get("documents", [])
    print(f"Birth Certificate (Update - Removed) docs: {len(birth_upd_docs)}")
    assert len(birth_upd_docs) == 0, f"Expected 0 docs for Birth Certificate Update, got {len(birth_upd_docs)}"

    # 2.4 Aadhaar Card (New: 3 docs [family caste cert removed], Update Address: 2 docs)
    res_adh_new = client.get("/api/services/aadhaar-card/documents?type=new")
    assert res_adh_new.status_code == 200
    adh_new_docs = res_adh_new.get_json().get("documents", [])
    print(f"Aadhaar Card (New) docs: {len(adh_new_docs)}")
    assert len(adh_new_docs) == 3, f"Expected 3 docs for Aadhaar New, got {len(adh_new_docs)}"
    assert "doc_family_caste_cert" not in [d["document_id"] for d in adh_new_docs]

    res_adh_addr = client.get("/api/services/aadhaar-card/documents?type=update&sub_operation=address")
    assert res_adh_addr.status_code == 200
    adh_addr_docs = res_adh_addr.get_json().get("documents", [])
    print(f"Aadhaar Card (Update Address) docs: {len(adh_addr_docs)}")
    assert len(adh_addr_docs) == 2, f"Expected 2 docs for Aadhaar Address Update, got {len(adh_addr_docs)}"

    # 2.5 PAN Card (New: 4 docs, Update Reprint: 1 doc)
    res_pan_new = client.get("/api/services/pan-card/documents?type=new")
    assert res_pan_new.status_code == 200
    pan_new_docs = res_pan_new.get_json().get("documents", [])
    print(f"PAN Card (New) docs: {len(pan_new_docs)}")
    assert len(pan_new_docs) == 4, f"Expected 4 docs for PAN New, got {len(pan_new_docs)}"

    res_pan_rep = client.get("/api/services/pan-card/documents?type=update&sub_operation=reprint")
    assert res_pan_rep.status_code == 200
    pan_rep_docs = res_pan_rep.get_json().get("documents", [])
    print(f"PAN Card (Update Reprint) docs: {len(pan_rep_docs)}")
    assert len(pan_rep_docs) == 1, f"Expected 1 doc for PAN Reprint, got {len(pan_rep_docs)}"

    # 2.6 Voter ID Card (New: 3 docs, Update Shifting: 2 docs)
    res_vot_new = client.get("/api/services/voter-id-card/documents?type=new")
    assert res_vot_new.status_code == 200
    vot_new_docs = res_vot_new.get_json().get("documents", [])
    print(f"Voter ID Card (New) docs: {len(vot_new_docs)}")
    assert len(vot_new_docs) == 3, f"Expected 3 docs for Voter ID New, got {len(vot_new_docs)}"

    res_vot_shift = client.get("/api/services/voter-id-card/documents?type=update&sub_operation=shifting")
    assert res_vot_shift.status_code == 200
    vot_shift_docs = res_vot_shift.get_json().get("documents", [])
    print(f"Voter ID Card (Update Shifting) docs: {len(vot_shift_docs)}")
    assert len(vot_shift_docs) == 2, f"Expected 2 docs for Voter ID Shifting, got {len(vot_shift_docs)}"

    # 2.7 Scholarship Application (New Only: 11 docs [nativity cert replaced with father & mother aadhaar])
    res_sch = client.get("/api/services/scholarship-application/documents?type=new")
    assert res_sch.status_code == 200
    sch_docs = res_sch.get_json().get("documents", [])
    print(f"Scholarship Application (New) docs: {len(sch_docs)}")
    assert len(sch_docs) == 11, f"Expected 11 docs for Scholarship Application, got {len(sch_docs)}"
    assert "doc_father_aadhaar" in [d["document_id"] for d in sch_docs]
    assert "doc_mother_aadhaar" in [d["document_id"] for d in sch_docs]
    assert "doc_nativity_cert" not in [d["document_id"] for d in sch_docs]
    assert "doc_correction_proof" not in [d["document_id"] for d in sch_docs]

    # 2.8 Ration Card (New: 3 docs [birth & death certs removed], Update Member Addition: 2 docs [birth & marriage certs removed])
    res_rat_new = client.get("/api/services/ration-card/documents?type=new")
    assert res_rat_new.status_code == 200
    rat_new_docs = res_rat_new.get_json().get("documents", [])
    print(f"Ration Card (New) docs: {len(rat_new_docs)}")
    assert len(rat_new_docs) == 3, f"Expected 3 docs for Ration Card New, got {len(rat_new_docs)}"
    assert "doc_birth_cert" not in [d["document_id"] for d in rat_new_docs]
    assert "doc_death_cert" not in [d["document_id"] for d in rat_new_docs]

    res_rat_add = client.get("/api/services/ration-card/documents?type=update&sub_operation=member_addition")
    assert res_rat_add.status_code == 200
    rat_add_docs = res_rat_add.get_json().get("documents", [])
    print(f"Ration Card (Update Member Addition) docs: {len(rat_add_docs)}")
    assert len(rat_add_docs) == 2, f"Expected 2 docs for Ration Card Member Addition, got {len(rat_add_docs)}"
    assert "doc_birth_cert" not in [d["document_id"] for d in rat_add_docs]
    assert "doc_marriage_cert" not in [d["document_id"] for d in rat_add_docs]

    # 2.9 Master Overview Catalog (Restored on "Clear Selection")
    res_docs = client.get("/api/services/government-document-verification/documents")
    assert res_docs.status_code == 200
    docs_data = res_docs.get_json()
    documents = docs_data.get("documents", [])
    print(f"Master overview catalog docs: {len(documents)}")
    assert len(documents) == 18, f"Expected 18 documents, got {len(documents)}"
    print("All service-wise document checklists verified successfully!")

    print("\n=== TEST 3: User Authentication & Token Generation ===")
    test_email = "nirishapriyaarepalli16@gmail.com"
    users_col = get_users_collection()
    user = users_col.find_one({"email": test_email})
    if not user:
        user_id = "usr_nirishapriya"
        users_col.insert_one({
            "_id": user_id,
            "name": "Nirisha Priya",
            "email": test_email,
            "password_hash": AuthService.hash_password("Password123!")
        })
    else:
        user_id = str(user["_id"])
    token = AuthService.generate_token(user_id, test_email, "Nirisha Priya")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Token generated for user: {user_id}")

    print("\n=== TEST 4: Upload Multiple Documents in One Session ===")
    import uuid
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"

    # Document 1: Aadhaar Card sample file
    aadhaar_content = b"%PDF-1.4 Government of India Unique Identification Authority of India UIDAI Aadhaar 1234 5678 9012"
    upload1_data = {
        "file": (io.BytesIO(aadhaar_content), "aadhaar_card_test.pdf"),
        "service_id": "srv_gov_doc_verify",
        "document_id": "doc_aadhaar",
        "session_id": session_id
    }
    res_up1 = client.post("/api/uploads", data=upload1_data, headers=headers, content_type="multipart/form-data")
    assert res_up1.status_code in [200, 201], f"Upload 1 failed: {res_up1.get_json()}"
    print(f"Uploaded Aadhaar: {res_up1.get_json().get('upload', {}).get('original_filename')}")

    # Document 2: PAN Card sample file
    pan_content = b"%PDF-1.4 Income Tax Department Government of India Permanent Account Number ABCDE1234F"
    upload2_data = {
        "file": (io.BytesIO(pan_content), "pan_card_test.pdf"),
        "service_id": "srv_gov_doc_verify",
        "document_id": "doc_pan",
        "session_id": session_id
    }
    res_up2 = client.post("/api/uploads", data=upload2_data, headers=headers, content_type="multipart/form-data")
    assert res_up2.status_code in [200, 201], f"Upload 2 failed: {res_up2.get_json()}"
    print(f"Uploaded PAN: {res_up2.get_json().get('upload', {}).get('original_filename')}")

    # Document 3: Father's Aadhaar Card sample file
    father_aadhaar_content = b"%PDF-1.4 Government of India Unique Identification Authority of India UIDAI Father Aadhaar 9876 5432 1098"
    upload3_data = {
        "file": (io.BytesIO(father_aadhaar_content), "father_aadhaar_test.pdf"),
        "service_id": "srv_gov_doc_verify",
        "document_id": "doc_father_aadhaar",
        "session_id": session_id
    }
    res_up3 = client.post("/api/uploads", data=upload3_data, headers=headers, content_type="multipart/form-data")
    assert res_up3.status_code in [200, 201], f"Upload 3 failed: {res_up3.get_json()}"
    print(f"Uploaded Father's Aadhaar: {res_up3.get_json().get('upload', {}).get('original_filename')}")

    # Document 4: Address Proof sample file (Electricity Bill uploaded to Address Proof slot)
    elec_content = b"%PDF-1.4 Electricity Bill Power Distribution Company Limited Consumer No 12345678 Service Connection Address Proof"
    upload4_data = {
        "file": (io.BytesIO(elec_content), "electricity_bill_test.pdf"),
        "service_id": "srv_gov_doc_verify",
        "document_id": "doc_address_proof",
        "session_id": session_id
    }
    res_up4 = client.post("/api/uploads", data=upload4_data, headers=headers, content_type="multipart/form-data")
    assert res_up4.status_code in [200, 201], f"Upload 4 failed: {res_up4.get_json()}"
    print(f"Uploaded Address Proof (Electricity Bill): {res_up4.get_json().get('upload', {}).get('original_filename')}")

    print("\n=== TEST 5: Run Verification Pipeline for Common Service ===")
    run_payload = {
        "session_id": session_id,
        "service_id": "srv_gov_doc_verify"
    }
    res_run = client.post("/api/verification/run", json=run_payload, headers=headers)
    assert res_run.status_code == 200, f"Verification run failed: {res_run.get_json()}"
    run_data = res_run.get_json()
    sess_summary = run_data.get("session", {})
    doc_results = run_data.get("document_results", [])
    print(f"Session overall status: {sess_summary.get('overall_status')}")
    print(f"Total documents evaluated: {sess_summary.get('total_required')}")
    print(f"Ready count: {sess_summary.get('ready_count')}")
    print(f"Document results count: {len(doc_results)}")
    assert len(doc_results) == 4, f"Expected 4 document results, got {len(doc_results)}"
    for r in doc_results:
        print(f" - {r.get('document_name')}: Status={r.get('status')}, Detected={r.get('detected_name')}")

    print("\n=== TEST 6: Fetch Verification Results Report ===")
    res_rep = client.get(f"/api/verification/results/{session_id}", headers=headers)
    assert res_rep.status_code == 200, f"Report fetch failed: {res_rep.get_json()}"
    rep_data = res_rep.get_json()
    print("Report fetched successfully without unauthorized error!")
    assert rep_data.get("session", {}).get("session_id") == session_id

    print("\n=== TEST 7: Fetch My Verifications History ===")
    res_hist = client.get("/api/verification/my-verifications", headers=headers)
    assert res_hist.status_code == 200, f"History fetch failed: {res_hist.get_json()}"
    hist_data = res_hist.get_json()
    verifications = hist_data.get("verifications", [])
    print(f"My Verifications count: {len(verifications)}")
    matched_session = [v for v in verifications if v.get("session_id") == session_id]
    assert len(matched_session) > 0, "Current session not found in My Verifications"
    print(f"Found session in history: {matched_session[0].get('service_name')} ({matched_session[0].get('ready_count')}/{matched_session[0].get('total_required')})")

    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_full_unified_flow()
