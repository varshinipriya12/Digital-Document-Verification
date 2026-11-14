from flask import Blueprint, jsonify, request
from database.mongodb import (
    get_services_collection,
    get_documents_collection,
    get_service_documents_collection
)

services_bp = Blueprint("services", __name__, url_prefix="/api/services")

@services_bp.route("", methods=["GET"])
def list_services():
    """Fetch ALL active official government services from MongoDB with bilingual support."""
    services_col = get_services_collection()
    services_cursor = services_col.find({
        "is_active": True,
        "_id": {"$ne": "srv_doc_matching_test"},
        "slug": {"$ne": "document-matching-verification"}
    })

    result = []
    for srv in services_cursor:
        if srv.get("name") and "Document Text Extraction" in srv.get("name"):
            continue
        result.append({
            "id": str(srv["_id"]),
            "name": srv.get("name"),
            "name_te": srv.get("name_te"),
            "slug": srv.get("slug"),
            "description": srv.get("description"),
            "description_te": srv.get("description_te"),
            "department": srv.get("department"),
            "department_te": srv.get("department_te"),
            "icon": srv.get("icon", "🏛️"),
            "has_update": srv.get("has_update", True),
            "official_portal_url": srv.get("official_portal_url")
        })

    return jsonify({"services": result, "count": len(result)}), 200


@services_bp.route("/<slug>", methods=["GET"])
def get_service_by_slug(slug):
    """Fetch details of a single government service by slug or _id."""
    services_col = get_services_collection()
    srv = services_col.find_one({"slug": slug, "is_active": True})

    if not srv:
        srv = services_col.find_one({"_id": slug})

    if not srv:
        srv = services_col.find_one({"slug": "government-document-verification"}) or services_col.find_one({"_id": "srv_gov_doc_verify"})

    if not srv:
        return jsonify({"error": "Government service not found."}), 404

    return jsonify({
        "service": {
            "id": str(srv["_id"]),
            "name": srv.get("name"),
            "name_te": srv.get("name_te"),
            "slug": srv.get("slug"),
            "description": srv.get("description"),
            "description_te": srv.get("description_te"),
            "department": srv.get("department"),
            "department_te": srv.get("department_te"),
            "icon": srv.get("icon", "🏛️"),
            "has_update": srv.get("has_update", True),
            "official_portal_url": srv.get("official_portal_url")
        }
    }), 200


@services_bp.route("/<slug>/documents", methods=["GET"])
def get_service_documents(slug):
    """
    Fetch required documents for a specific service dynamically from MongoDB.
    Supports filtering by application_type ('new' vs 'update') and optional sub_operation.
    """
    app_type = request.args.get("application_type") or request.args.get("type") or "new"
    app_type = app_type.strip().lower()
    sub_op = request.args.get("sub_operation") or request.args.get("sub_type") or ""
    sub_op = sub_op.strip().lower()

    services_col = get_services_collection()
    srv = services_col.find_one({"slug": slug})
    if not srv:
        srv = services_col.find_one({"_id": slug})

    if not srv:
        srv = services_col.find_one({"slug": "government-document-verification"}) or services_col.find_one({"_id": "srv_gov_doc_verify"})

    if not srv:
        return jsonify({"error": "Government service not found."}), 404

    service_id = str(srv["_id"])
    service_docs_col = get_service_documents_collection()
    documents_col = get_documents_collection()

    # Query mapping between service and documents, respecting application_type & sub_operation
    if service_id == "srv_gov_doc_verify" or slug == "government-document-verification":
        # Master overview catalog
        mappings = list(service_docs_col.find({"service_id": "srv_gov_doc_verify"}).sort("display_order", 1))
    elif app_type == "update" and not srv.get("has_update", True):
        # Service does not support update option (e.g. Scholarship, Birth Certificate)
        mappings = []
    else:
        query = {"service_id": service_id, "application_type": app_type}
        if sub_op:
            query["sub_operation"] = sub_op
            mappings = list(service_docs_col.find(query).sort("display_order", 1))
        else:
            # First try empty sub_operation
            mappings = list(service_docs_col.find({"service_id": service_id, "application_type": app_type, "sub_operation": ""}).sort("display_order", 1))
            if not mappings:
                # If no empty sub_operation, find all sub_operations available and pick the first one's documents
                first_mapping = service_docs_col.find_one({"service_id": service_id, "application_type": app_type})
                if first_mapping:
                    default_sub_op = first_mapping.get("sub_operation", "")
                    mappings = list(service_docs_col.find({"service_id": service_id, "application_type": app_type, "sub_operation": default_sub_op}).sort("display_order", 1))
                else:
                    mappings = []

    required_documents = []
    for m in mappings:
        doc_id = m["document_id"]
        doc = documents_col.find_one({"_id": doc_id})
        if doc:
            badge_type = m.get("badge_type")
            if not badge_type:
                badge_type = "mandatory" if m.get("is_mandatory", True) else "optional"

            required_documents.append({
                "document_id": str(doc["_id"]),
                "name": doc.get("name"),
                "name_te": doc.get("name_te"),
                "slug": doc.get("slug"),
                "icon": doc.get("icon", "📄"),
                "description": doc.get("description"),
                "description_te": doc.get("description_te"),
                "is_mandatory": m.get("is_mandatory", True),
                "badge_type": badge_type,
                "application_type": m.get("application_type", app_type),
                "sub_operation": m.get("sub_operation", sub_op),
                "expected_keywords": doc.get("expected_keywords", [])
            })

    return jsonify({
        "service": {
            "id": service_id,
            "name": srv.get("name"),
            "name_te": srv.get("name_te"),
            "slug": srv.get("slug"),
            "icon": srv.get("icon", "🏛️"),
            "has_update": srv.get("has_update", True),
            "application_type": app_type,
            "sub_operation": sub_op,
            "official_portal_url": srv.get("official_portal_url")
        },
        "documents": required_documents
    }), 200
