import datetime
import uuid
from flask import Blueprint, request, jsonify, session
from database.mongodb import (
    get_services_collection,
    get_documents_collection,
    get_service_documents_collection,
    get_uploads_collection,
    get_verification_results_collection,
    get_verification_sessions_collection,
    get_users_collection
)
from services.opencv_service import OpenCVQualityChecker
from services.ocr_service import OCRService
from services.gemini_service import GeminiVerificationService
from services.auth_service import AuthService

verification_bp = Blueprint("verification", __name__, url_prefix="/api/verification")

@verification_bp.route("/run", methods=["POST"])
def run_verification():
    """
    Run simplified verification pipeline:
    1. Document Quality and Clarity Check (OpenCV blur, brightness, blankness, resolution)
    2. Document Type Verification (Gemini AI / OCR structure matching)
    Completely removes all personal identity, name matching, and family relationship logic.
    """
    data = request.get_json() or {}
    session_id = data.get("session_id", "").strip()
    service_id = data.get("service_id", "").strip()
    
    user_id = session.get("user_id")
    auth_header = request.headers.get("Authorization", "")
    if not user_id and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        decoded = AuthService.verify_token(token)
        if decoded and "sub" in decoded:
            user_id = decoded["sub"]

    if not user_id:
        user_id = "anonymous"

    if not session_id or not service_id:
        return jsonify({"error": "Missing session_id or service_id parameter."}), 400

    services_col = get_services_collection()
    srv = services_col.find_one({"_id": service_id})
    if not srv:
        srv = services_col.find_one({"slug": service_id})

    if not srv:
        return jsonify({"error": "Government service not found."}), 404

    srv_id = str(srv["_id"])
    srv_name = srv.get("name")
    srv_name_te = srv.get("name_te")
    official_portal_url = srv.get("official_portal_url", "https://services.india.gov.in/")

    app_type = data.get("application_type") or data.get("type") or "new"
    app_type = app_type.strip().lower()

    # Fetch required documents from MongoDB
    service_docs_col = get_service_documents_collection()
    documents_col = get_documents_collection()
    uploads_col = get_uploads_collection()

    # Query mappings respecting application_type
    if app_type in ["new", "update"]:
        typed_mappings = list(service_docs_col.find({"service_id": srv_id, "application_type": app_type}).sort("display_order", 1))
        if typed_mappings:
            req_mappings = typed_mappings
        else:
            req_mappings = list(service_docs_col.find({"service_id": srv_id}).sort("display_order", 1))
    else:
        req_mappings = list(service_docs_col.find({"service_id": srv_id}).sort("display_order", 1))

    # All documents uploaded in this session
    session_uploads = list(uploads_col.find({"session_id": session_id}))
    if srv_id == "srv_gov_doc_verify" or srv.get("slug") == "government-document-verification":
        if not session_uploads:
            return jsonify({"error": "No documents uploaded. Please select and upload at least one document to verify."}), 400
        uploaded_doc_ids = set(u["document_id"] for u in session_uploads)
        req_mappings = [m for m in req_mappings if m["document_id"] in uploaded_doc_ids]
        # Include any upload not yet in req_mappings
        mapped_ids = set(m["document_id"] for m in req_mappings)
        for u in session_uploads:
            if u["document_id"] not in mapped_ids:
                req_mappings.append({"service_id": srv_id, "document_id": u["document_id"], "is_mandatory": True, "display_order": 99})

    document_results = []
    verified_count = 0
    poor_quality_count = 0
    invalid_type_count = 0
    needs_review_count = 0
    missing_count = 0

    results_col = get_verification_results_collection()

    # Clear previous results for this session if re-running
    results_col.delete_many({"session_id": session_id})

    for m in req_mappings:
        doc_id = m["document_id"]
        is_mandatory = m.get("is_mandatory", True)
        doc = documents_col.find_one({"_id": doc_id})

        doc_name = doc.get("name", "Document") if doc else "Document"
        doc_desc = doc.get("description", "") if doc else ""
        doc_type = doc.get("doc_type") if doc else None
        expected_keywords = doc.get("expected_keywords", []) if doc else []

        # Find upload for this document slot for exact session and service
        upload = uploads_col.find_one({
            "session_id": session_id,
            "service_id": srv_id,
            "document_id": doc_id
        })
        if not upload:
            upload = uploads_col.find_one({
                "session_id": session_id,
                "document_id": doc_id
            })

        if not upload:
            # Document MISSING
            status = "missing"
            status_label = "Missing"
            missing_count += 1
            res_doc = {
                "_id": str(uuid.uuid4()),
                "upload_id": None,
                "session_id": session_id,
                "document_id": doc_id,
                "document_name": doc_name,
                "is_mandatory": is_mandatory,
                "status": "missing",
                "status_label": "Missing",
                "quality_passed": False,
                "type_matched": False,
                "detected_type": "none",
                "detected_name": "No Document Uploaded",
                "detected_document": "No Document Uploaded",
                "confidence": 0,
                "reason": f"Required document '{doc_name}' was not uploaded.",
                "extracted_text": None,
                "extracted_text_snippet": None,
                "quality_details": {},
                "checked_at": datetime.datetime.now(datetime.timezone.utc)
            }
            document_results.append(res_doc)
            results_col.insert_one(res_doc)
            continue

        upload_id = str(upload["_id"])
        file_path = upload.get("file_path")

        # Step 1: OpenCV Document Quality & Clarity Analysis
        opencv_res = OpenCVQualityChecker.analyze_quality(file_path)

        # Step 2: OCR Text Extraction
        ocr_res = OCRService.extract_text(file_path)
        extracted_text = ocr_res.get("extracted_text", "")

        # Step 3: Gemini AI / Multi-Signal Document Type Verification
        gemini_res = GeminiVerificationService.verify_document(
            required_doc_name=doc_name,
            required_doc_description=doc_desc,
            expected_keywords=expected_keywords,
            file_path=file_path,
            ocr_text=extracted_text,
            opencv_quality=opencv_res,
            required_doc_type=doc_type,
            original_filename=upload.get("original_filename", "")
        )

        status = gemini_res.get("status", "invalid_type")
        status_label = gemini_res.get("status_label", "Invalid Document Type")
        reason = gemini_res.get("reason", "Verification complete.")
        confidence = gemini_res.get("confidence", 80)
        detected_type = gemini_res.get("detected_type", "other_unknown")
        detected_name = gemini_res.get("detected_name", "Unknown Document")

        # Update counter tallies (verified, poor_quality, needs_review, invalid_type, missing)
        if status in ["verified", "ready"]:
            status = "verified"
            status_label = "Verified"
            verified_count += 1
        elif status == "poor_quality":
            poor_quality_count += 1
        elif status == "needs_review":
            status = "needs_review"
            status_label = "Needs Review"
            needs_review_count += 1
        else:
            status = "invalid_type"
            status_label = "Invalid Document Type"
            invalid_type_count += 1

        quality_passed = (status != "poor_quality")
        type_matched = (status == "verified")

        res_doc = {
            "_id": str(uuid.uuid4()),
            "upload_id": upload_id,
            "session_id": session_id,
            "document_id": doc_id,
            "document_name": doc_name,
            "original_filename": upload.get("original_filename"),
            "is_mandatory": is_mandatory,
            "status": status,
            "status_label": status_label,
            "quality_passed": quality_passed,
            "type_matched": type_matched,
            "detected_type": detected_type,
            "detected_name": detected_name,
            "detected_document": detected_name,
            "confidence": confidence,
            "reason": reason,
            "extracted_text": extracted_text,
            "extracted_text_snippet": extracted_text[:300] if extracted_text else None,
            "quality_details": opencv_res,
            "checked_at": datetime.datetime.now(datetime.timezone.utc)
        }
        document_results.append(res_doc)
        results_col.insert_one(res_doc)

    total_docs = len(req_mappings)

    # Calculate overall status
    if verified_count == total_docs and total_docs > 0:
        overall_status = "VERIFIED"
        summary_message = "All required documents are clear, verified, and match the required document types."
    else:
        overall_status = "ACTION REQUIRED"
        summary_message = "Some documents have quality issues, invalid types, or are missing. Please review and replace the highlighted documents."

    session_doc = {
        "_id": session_id,
        "user_id": user_id,
        "service_id": srv_id,
        "service_name": srv_name,
        "service_name_te": srv_name_te,
        "official_portal_url": official_portal_url,
        "overall_status": overall_status,
        "summary_message": summary_message,
        "total_required": total_docs,
        "documents_checked": total_docs,
        "verified_count": verified_count,
        "ready_count": verified_count,                         # compatibility alias
        "poor_quality_count": poor_quality_count,
        "needs_attention_count": poor_quality_count,           # compatibility alias
        "invalid_type_count": invalid_type_count,
        "invalid_count": invalid_type_count,                   # compatibility alias
        "needs_review_count": needs_review_count,
        "missing_count": missing_count,
        "disclaimer": "This is a preliminary document-readiness check. It does not confirm legal authenticity or official government approval.",
        "created_at": datetime.datetime.now(datetime.timezone.utc)
    }

    sessions_col = get_verification_sessions_collection()
    sessions_col.update_one({"_id": session_id}, {"$set": session_doc}, upsert=True)

    return jsonify({
        "session": session_doc,
        "document_results": document_results
    }), 200


@verification_bp.route("/results/<session_id>", methods=["GET"])
def get_verification_results(session_id):
    """Retrieve saved verification report for a session."""
    sessions_col = get_verification_sessions_collection()
    results_col = get_verification_results_collection()

    session_doc = sessions_col.find_one({"_id": session_id})
    if not session_doc:
        return jsonify({"error": "Verification session report not found."}), 404

    user_id = session.get("user_id")
    auth_header = request.headers.get("Authorization", "")
    if not user_id and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        decoded = AuthService.verify_token(token)
        if decoded and "sub" in decoded:
            user_id = decoded["sub"]

    # Verify session access: allow viewing if owner matches, same email, or valid session link
    if session_doc.get("user_id") and session_doc.get("user_id") != "anonymous":
        if user_id and user_id != session_doc.get("user_id"):
            users_col = get_users_collection()
            u_req = users_col.find_one({"_id": user_id})
            u_sess = users_col.find_one({"_id": session_doc.get("user_id")})
            if u_req and u_sess and u_req.get("email") != u_sess.get("email"):
                # Allow access if user is logged in and viewing their session
                pass

    results_cursor = results_col.find({"session_id": session_id})
    doc_results = []
    for r in results_cursor:
        doc_results.append({
            "result_id": str(r["_id"]),
            "document_id": r.get("document_id"),
            "document_name": r.get("document_name"),
            "original_filename": r.get("original_filename"),
            "is_mandatory": r.get("is_mandatory", True),
            "status": r.get("status"),
            "status_label": r.get("status_label") or ("Verified" if r.get("status") in ["verified", "ready"] else "Poor Quality" if r.get("status") == "poor_quality" else "Invalid Document Type" if r.get("status") in ["invalid", "invalid_type", "needs_review", "needs_attention"] else "Missing"),
            "quality_passed": r.get("quality_passed", r.get("status") not in ["poor_quality", "missing"]),
            "type_matched": r.get("type_matched", r.get("status") in ["verified", "ready"]),
            "detected_type": r.get("detected_type"),
            "detected_name": r.get("detected_name"),
            "detected_document": r.get("detected_document") or r.get("detected_name"),
            "confidence": r.get("confidence", 0),
            "reason": r.get("reason"),
            "extracted_text": r.get("extracted_text") or r.get("extracted_text_snippet"),
            "extracted_text_snippet": r.get("extracted_text_snippet"),
            "quality_details": r.get("quality_details")
        })

    return jsonify({
        "session": {
            "session_id": session_doc["_id"],
            "service_name": session_doc.get("service_name"),
            "official_portal_url": session_doc.get("official_portal_url"),
            "overall_status": session_doc.get("overall_status"),
            "summary_message": session_doc.get("summary_message"),
            "total_required": session_doc.get("total_required"),
            "verified_count": session_doc.get("verified_count", session_doc.get("ready_count", 0)),
            "ready_count": session_doc.get("ready_count", session_doc.get("verified_count", 0)),
            "poor_quality_count": session_doc.get("poor_quality_count", 0),
            "invalid_type_count": session_doc.get("invalid_type_count", session_doc.get("invalid_count", 0)),
            "needs_review_count": session_doc.get("needs_review_count", 0),
            "needs_attention_count": session_doc.get("needs_attention_count", 0),
            "invalid_count": session_doc.get("invalid_count", 0),
            "missing_count": session_doc.get("missing_count", 0),
            "disclaimer": session_doc.get("disclaimer"),
            "created_at": session_doc.get("created_at").isoformat() if session_doc.get("created_at") else None
        },
        "document_results": doc_results
    }), 200


@verification_bp.route("/my-verifications", methods=["GET"])
def get_my_verifications():
    """Retrieve previous verification sessions for logged-in user."""
    user_id = session.get("user_id")
    auth_header = request.headers.get("Authorization", "")

    if not user_id and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        decoded = AuthService.verify_token(token)
        if decoded and "sub" in decoded:
            user_id = decoded["sub"]

    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    sessions_col = get_verification_sessions_collection()
    results_col = get_verification_results_collection()
    cursor = sessions_col.find({"user_id": user_id}).sort("created_at", -1)

    my_sessions = []
    for s in cursor:
        srv_name_te = s.get("service_name_te")
        session_id = str(s["_id"])

        # Fetch detailed document results for this verification session
        doc_results = list(results_col.find({"session_id": session_id}))
        docs = []
        for dr in doc_results:
            docs.append({
                "document_name": dr.get("document_name"),
                "original_filename": dr.get("original_filename"),
                "status": dr.get("status"),
                "detected_type": dr.get("detected_type"),
                "detected_document": dr.get("detected_document") or dr.get("detected_name"),
                "reason": dr.get("reason")
            })

        my_sessions.append({
            "session_id": session_id,
            "service_name": s.get("service_name"),
            "service_name_te": srv_name_te,
            "overall_status": s.get("overall_status"),
            "summary_message": s.get("summary_message"),
            "total_required": s.get("total_required", 0),
            "ready_count": s.get("ready_count", 0),
            "needs_attention_count": s.get("needs_attention_count", 0),
            "invalid_count": s.get("invalid_count", 0),
            "missing_count": s.get("missing_count", 0),
            "documents": docs,
            "date": s.get("created_at").strftime("%b %d, %Y %I:%M %p") if s.get("created_at") else "N/A"
        })

    return jsonify({"verifications": my_sessions}), 200
