import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-gov-doc-verification-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key-gov-doc-verification-2026")
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/gov_doc_verification")
    DB_NAME = os.getenv("DB_NAME", "gov_doc_verification")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    # SMTP / Email Configuration for OTPs & Alerts
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USERNAME", "noreply@digitaldocverify.gov.in"))
    
    # Upload limits
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB max size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # Quality thresholds for OpenCV
    BLUR_THRESHOLD = float(os.getenv("BLUR_THRESHOLD", "80.0"))  # Laplacian variance threshold
    MIN_BRIGHTNESS = int(os.getenv("MIN_BRIGHTNESS", "35"))
    MAX_BRIGHTNESS = int(os.getenv("MAX_BRIGHTNESS", "248"))
    MIN_DIMENSION = int(os.getenv("MIN_DIMENSION", "300"))

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
