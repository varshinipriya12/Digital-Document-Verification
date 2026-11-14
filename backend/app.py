import os
import sys
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from config import Config
from database.mongodb import get_services_collection
from database.seed import seed_database
from routes.auth import auth_bp
from routes.services import services_bp
from routes.uploads import uploads_bp
from routes.verification import verification_bp

# Define frontend static directory relative to backend
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.config.from_object(Config)

# Enable CORS for full REST API access
CORS(app, supports_credentials=True)

# Register API blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(services_bp)
app.register_blueprint(uploads_bp)
app.register_blueprint(verification_bp)

# Auto-seed database if empty on app startup
try:
    services_col = get_services_collection()
    if services_col.count_documents({}) == 0:
        print("Database is empty. Auto-seeding initial government services and documents...")
        seed_database()
except Exception as e:
    print(f"Notice on startup auto-seed check: {e}")

# Frontend static page routes
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    # Serve requested static html/css/js asset if file exists
    full_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, filename)
    # Default to index.html for SPA routing
    return send_from_directory(FRONTEND_DIR, "index.html")

# Global Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "Uploaded file exceeds maximum limit of 8 MB."}), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "An internal server error occurred. Please try again later."}), 500

if __name__ == "__main__":
    print(f"Starting Digital Document Verification Flask Server on http://localhost:5000")
    print(f"Serving frontend from {FRONTEND_DIR}")
    app.run(host="0.0.0.0", port=5000, debug=True)
