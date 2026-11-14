import os
import uuid
import datetime
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from config import Config
from database.mongodb import get_uploads_collection

uploads_bp = Blueprint("uploads", __name__, url_prefix="/api/uploads")

def allowed_file(filename: str) -> bool:
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS

@uploads_bp.route("", methods=["POST"])
def upload_file():
    """
    Handle single file upload for a service document slot.
    Validates file type and size (<= 8MB).
    Saves file with UUID to prevent security issues.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part attached in request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    service_id = request.form.get("service_id", "").strip()
    document_id = request.form.get("document_id", "").strip()
    session_id = request.form.get("session_id", "").strip() or str(uuid.uuid4())
    user_id = session.get("user_id", "anonymous")

    if not service_id or not document_id:
        return jsonify({"error": "Missing service_id or document_id parameters."}), 400

    original_filename = secure_filename(file.filename)
    if not allowed_file(original_filename):
        return jsonify({
            "error": "Unsupported file format. Please upload a PDF, JPG, JPEG, or PNG file."
        }), 400

    # Read content to check length
    file_bytes = file.read()
    file_size = len(file_bytes)

    if file_size > Config.MAX_CONTENT_LENGTH:
        return jsonify({
            "error": f"File size ({round(file_size/(1024*1024), 2)} MB) exceeds maximum allowed limit of 8 MB."
        }), 400

    if file_size == 0:
        return jsonify({"error": "Uploaded file is empty (0 bytes)."}), 400

    # Save file with unique UUID storage filename
    ext = original_filename.rsplit('.', 1)[1].lower()
    upload_id = str(uuid.uuid4())
    stored_filename = f"{upload_id}.{ext}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, stored_filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    uploads_col = get_uploads_collection()

    # Delete previous upload for the same session and document_id if replacing file
    uploads_col.delete_many({
        "session_id": session_id,
        "document_id": document_id
    })

    # Clear old verification result for this document slot in the session
    from database.mongodb import get_verification_results_collection
    results_col = get_verification_results_collection()
    results_col.delete_many({
        "session_id": session_id,
        "document_id": document_id
    })

    upload_doc = {
        "_id": upload_id,
        "user_id": user_id,
        "session_id": session_id,
        "service_id": service_id,
        "document_id": document_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_path": file_path,
        "file_type": ext,
        "file_size": file_size,
        "uploaded_at": datetime.datetime.now(datetime.timezone.utc)
    }
    uploads_col.insert_one(upload_doc)

    return jsonify({
        "message": "File uploaded successfully.",
        "status_note": "File uploaded. Document type will be checked during verification.",
        "upload": {
            "upload_id": upload_id,
            "session_id": session_id,
            "document_id": document_id,
            "original_filename": original_filename,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "file_type": ext
        }
    }), 201


@uploads_bp.route("/<session_id>", methods=["GET"])
def get_session_uploads(session_id):
    """Retrieve list of uploads for a given verification session."""
    uploads_col = get_uploads_collection()
    cursor = uploads_col.find({"session_id": session_id})

    uploads_list = []
    for u in cursor:
        uploads_list.append({
            "upload_id": str(u["_id"]),
            "document_id": u.get("document_id"),
            "original_filename": u.get("original_filename"),
            "file_size_mb": round(u.get("file_size", 0) / (1024 * 1024), 2),
            "file_type": u.get("file_type"),
            "uploaded_at": u.get("uploaded_at").isoformat() if u.get("uploaded_at") else None
        })

    return jsonify({"session_id": session_id, "uploads": uploads_list}), 200


@uploads_bp.route("/<upload_id>", methods=["DELETE"])
def remove_upload(upload_id):
    """Remove uploaded document from disk and MongoDB."""
    uploads_col = get_uploads_collection()
    u = uploads_col.find_one({"_id": upload_id})
    if not u:
        return jsonify({"error": "Upload record not found."}), 404

    file_path = u.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            pass

    uploads_col.delete_one({"_id": upload_id})
    return jsonify({"message": "File removed successfully."}), 200
