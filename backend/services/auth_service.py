import datetime
import re
import bcrypt
import jwt
import requests
from config import Config

class AuthService:

    @staticmethod
    def validate_strong_password(password: str) -> tuple[bool, list[str]]:
        """
        Validate that password satisfies:
        1. At least 8 characters
        2. At least one uppercase letter (A-Z)
        3. At least one lowercase letter (a-z)
        4. At least one number (0-9)
        5. At least one special character (@, #, $, %, &, !, etc.)
        Returns (is_valid: bool, missing_requirements: list[str])
        """
        missing = []
        if not password or len(password) < 8:
            missing.append("At least 8 characters")
        if not re.search(r'[A-Z]', password or ""):
            missing.append("At least one uppercase letter (A–Z)")
        if not re.search(r'[a-z]', password or ""):
            missing.append("At least one lowercase letter (a–z)")
        if not re.search(r'[0-9]', password or ""):
            missing.append("At least one number (0–9)")
        if not re.search(r'[@#$%&!^&*()_+=\-\[\]{};:\'",.<>?/\\|`~]', password or ""):
            missing.append("At least one special character (@, #, $, %, &, !, etc.)")

        is_valid = len(missing) == 0
        return is_valid, missing

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a stored bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def generate_token(user_id: str, email: str, name: str) -> str:
        """Generate JWT authentication token for logged-in user."""
        payload = {
            "sub": user_id,
            "email": email,
            "name": name,
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> dict:
        """Decode and validate a JWT authentication token."""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired."}
        except jwt.InvalidTokenError:
            return {"error": "Invalid authentication token."}

    @staticmethod
    def get_google_user_info(access_token_or_code: str) -> dict:
        """
        Fetch Google User Profile from Google OAuth endpoint using access token or authorization code exchange.
        """
        try:
            # If access_token passed directly
            user_info_resp = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token_or_code}"},
                timeout=5
            )
            if user_info_resp.status_code == 200:
                return user_info_resp.json()
            return {"error": f"Failed to fetch Google user info: {user_info_resp.text}"}
        except Exception as e:
            return {"error": str(e)}
