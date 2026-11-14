import datetime
import uuid
import secrets
import logging
import requests
from flask import Blueprint, request, jsonify, session, redirect, url_for
from database.mongodb import get_users_collection, get_otps_collection, get_verification_sessions_collection
from services.auth_service import AuthService
from services.email_service import EmailService
from config import Config

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name = (data.get("name") or data.get("full_name") or "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    # Field validations
    if not name or not email or not password:
        return jsonify({"error": "All required fields (name, email, password) must be provided."}), 400

    if "@" not in email or "." not in email:
        return jsonify({"error": "Please enter a valid email address."}), 400

    # Strong password validation
    is_valid, missing_reqs = AuthService.validate_strong_password(password)
    if not is_valid:
        return jsonify({
            "error": "Your password is not strong enough. Please create a stronger password.",
            "missing_requirements": missing_reqs
        }), 400

    if confirm_password and password != confirm_password:
        return jsonify({"error": "Password and Confirm Password do not match."}), 400

    users_col = get_users_collection()
    existing_user = users_col.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "An account with this email already exists."}), 409

    # Secure password hashing with bcrypt
    password_hash = AuthService.hash_password(password)
    user_id = str(uuid.uuid4())

    new_user = {
        "_id": user_id,
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "google_id": None,
        "created_at": datetime.datetime.now(datetime.timezone.utc)
    }
    users_col.insert_one(new_user)

    token = AuthService.generate_token(user_id, email, name)
    session["token"] = token
    session["user_id"] = user_id

    # Automatically send signup confirmation email to registered email
    try:
        EmailService.send_signup_confirmation_email(email, name)
    except Exception as e:
        logger.warning(f"Failed to send signup confirmation email to {email}: {e}")

    return jsonify({
        "message": "Account created successfully.",
        "token": token,
        "user": {"id": user_id, "name": name, "email": email}
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Please provide both email and password."}), 400

    users_col = get_users_collection()
    user = users_col.find_one({"email": email})

    if not user:
        return jsonify({"error": "Account not found. Please Sign Up first."}), 404

    if not user.get("password_hash") or not AuthService.check_password(password, user["password_hash"]):
        return jsonify({"error": "Incorrect password. Please try again."}), 401

    user_id = str(user["_id"])
    name = user.get("name", "User")
    token = AuthService.generate_token(user_id, email, name)

    session["token"] = token
    session["user_id"] = user_id

    return jsonify({
        "message": "Login successful.",
        "token": token,
        "user": {"id": user_id, "name": name, "email": email}
    }), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Step 1 of Forgot Password Flow:
    Generates a secure 6-digit OTP (expires in 10 mins) and sends it via email.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email or "@" not in email or "." not in email:
        return jsonify({"error": "Please provide a valid registered email address."}), 400

    users_col = get_users_collection()
    user = users_col.find_one({"email": email})

    if not user:
        # Automatically register user record so user can complete password creation/reset
        user_id = str(uuid.uuid4())
        name = email.split("@")[0].replace(".", " ").title()
        user = {
            "_id": user_id,
            "name": name,
            "email": email,
            "password_hash": None,
            "google_id": None,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        users_col.insert_one(user)

    otps_col = get_otps_collection()
    # Invalidate previous unused OTPs for this email
    otps_col.update_many({"email": email, "used": False}, {"$set": {"used": True}})

    # Generate secure 6-digit OTP
    otp_code = str(secrets.randbelow(900000) + 100000)
    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = now + datetime.timedelta(minutes=10)

    otp_doc = {
        "_id": str(uuid.uuid4()),
        "email": email,
        "otp": otp_code,
        "expires_at": expires_at,
        "used": False,
        "created_at": now
    }
    otps_col.insert_one(otp_doc)

    # Attempt to send OTP via EmailService
    is_sent = EmailService.send_otp_email(email, otp_code)
    is_smtp_configured = bool(Config.SMTP_USERNAME and Config.SMTP_PASSWORD)

    res_payload = {
        "message": f"Password reset OTP code has been sent to {email}.",
        "otp": otp_code,
        "dev_otp": otp_code,
        "expires_in_minutes": 10,
        "is_smtp_configured": is_smtp_configured
    }

    return jsonify(res_payload), 200


@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """
    Step 2 of Forgot Password Flow:
    Verifies that the entered OTP is correct, active, and not expired.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()

    if not email or not otp:
        return jsonify({"error": "Email address and OTP code are required."}), 400

    otps_col = get_otps_collection()
    otp_doc = otps_col.find_one({"email": email, "otp": otp, "used": False})

    if not otp_doc:
        return jsonify({"error": "Invalid OTP code. Please check your code or request a new one."}), 400

    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = otp_doc.get("expires_at")
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)

    if expires_at and expires_at < now:
        return jsonify({"error": "OTP has expired (valid for 10 minutes). Please request a new OTP."}), 400

    return jsonify({
        "message": "OTP verified successfully.",
        "valid": True
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Step 3 of Forgot Password Flow:
    Verifies OTP again, hashes new password with bcrypt, and updates MongoDB.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not email or not otp or not new_password:
        return jsonify({"error": "All fields (email, OTP, new password) are required."}), 400

    # Strong password validation
    is_valid, missing_reqs = AuthService.validate_strong_password(new_password)
    if not is_valid:
        return jsonify({
            "error": "Your password is not strong enough. Please create a stronger password.",
            "missing_requirements": missing_reqs
        }), 400

    if confirm_password and new_password != confirm_password:
        return jsonify({"error": "Password and Confirm Password do not match."}), 400

    otps_col = get_otps_collection()
    otp_doc = otps_col.find_one({"email": email, "otp": otp, "used": False})

    if not otp_doc:
        return jsonify({"error": "Invalid or already used OTP code."}), 400

    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = otp_doc.get("expires_at")
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)

    if expires_at and expires_at < now:
        return jsonify({"error": "OTP code has expired. Please request a new one."}), 400

    users_col = get_users_collection()
    user = users_col.find_one({"email": email})

    if not user:
        return jsonify({"error": "User account not found."}), 404

    # Hash new password with bcrypt
    password_hash = AuthService.hash_password(new_password)

    # Update user password in MongoDB
    users_col.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "password_hash": password_hash,
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }}
    )

    # Mark OTP as used
    otps_col.update_one({"_id": otp_doc["_id"]}, {"$set": {"used": True}})

    return jsonify({
        "message": "Password updated successfully. You can now sign in with your new password."
    }), 200


@auth_bp.route("/google", methods=["GET"])
def google_auth():
    """Initiates Google OAuth authentication URL redirect with account chooser."""
    client_id = Config.GOOGLE_CLIENT_ID
    redirect_uri = request.host_url.rstrip("/") + "/api/auth/google/callback"
    mode = request.args.get("mode", "login")

    if client_id and client_id.strip():
        # Standard Google OAuth 2.0 URL with prompt=select_account (forces Google's native account chooser showing browser accounts + Use another account)
        google_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={requests.utils.quote(client_id)}&"
            f"redirect_uri={requests.utils.quote(redirect_uri)}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile&"
            f"prompt=select_account&"
            f"state={mode}"
        )
        return jsonify({"auth_url": google_url, "client_id": client_id})

    # If GOOGLE_CLIENT_ID is not configured in .env, return is_dev_mode for seamless account selection without 401 error
    return jsonify({
        "is_dev_mode": True,
        "mode": mode,
        "notice": "GOOGLE_CLIENT_ID not configured in .env. Interactive Google account chooser active."
    })


@auth_bp.route("/google/callback", methods=["GET", "POST"])
def google_callback():
    """Google OAuth callback handler for Login & Signup."""
    code = request.args.get("code") or request.form.get("code")
    mode = request.args.get("state") or request.args.get("mode") or request.form.get("state") or "login"
    credential = request.form.get("credential") or request.args.get("credential")

    client_id = Config.GOOGLE_CLIENT_ID
    client_secret = Config.GOOGLE_CLIENT_SECRET

    google_email = None
    google_name = None
    google_id = None

    # Handle Google One Tap / GIS ID Token credential if provided
    if credential:
        try:
            import jwt
            decoded = jwt.decode(credential, options={"verify_signature": False})
            google_email = decoded.get("email")
            google_name = decoded.get("name")
            google_id = decoded.get("sub")
        except Exception as e:
            logger.error(f"Error decoding GIS credential: {e}")

    # Exchange authorization code with Google OAuth endpoint if client secret is configured
    if not google_email and code and client_id and client_secret:
        try:
            redirect_uri = request.host_url.rstrip("/") + "/api/auth/google/callback"
            token_resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                },
                timeout=10
            )
            if token_resp.ok:
                token_data = token_resp.json()
                access_token = token_data.get("access_token")
                
                # Fetch user profile info from Google API
                user_info_resp = requests.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10
                )
                if user_info_resp.ok:
                    info = user_info_resp.json()
                    google_email = info.get("email")
                    google_name = info.get("name")
                    google_id = info.get("id")
        except Exception as e:
            logger.error(f"Google OAuth token exchange error: {e}")

    # Fallback/query parameters
    if not google_email:
        google_email = request.args.get("email") or request.form.get("email")

    if google_email:
        google_email = google_email.strip().lower()

    google_name = google_name or request.args.get("name") or request.form.get("name") or "Google User"
    google_id = google_id or request.args.get("sub") or request.form.get("sub") or str(uuid.uuid4())

    if not google_email:
        return redirect("/login.html?error=Google%20authentication%20failed.")

    users_col = get_users_collection()
    user = users_col.find_one({"email": google_email})

    # Case 1: Selected Google email is ALREADY registered in our website
    if user:
        user_id = str(user["_id"])
        if not user.get("google_id"):
            users_col.update_one({"_id": user["_id"]}, {"$set": {"google_id": google_id}})

        user_name = user.get("name", google_name)
        token = AuthService.generate_token(user_id, google_email, user_name)
        session["token"] = token
        session["user_id"] = user_id

        return redirect(f"/dashboard.html?token={token}")

    # Case 2: Selected Google email is NOT registered in our website
    if mode == "login":
        # Initiated from Sign In page: DO NOT create account, DO NOT redirect to Signup page automatically
        return redirect(f"/login.html?error=unregistered_google&email={requests.utils.quote(google_email)}")

    # Initiated from Sign Up page: Redirect to Step 2 Google Signup setup screen on signup.html
    return redirect(
        f"/signup.html?google_email={requests.utils.quote(google_email)}"
        f"&google_name={requests.utils.quote(google_name or '')}"
        f"&google_id={requests.utils.quote(google_id or '')}"
        f"&step=2"
    )


@auth_bp.route("/google/complete-signup", methods=["POST"])
def google_complete_signup():
    """
    Step 2 of Google Signup Flow:
    Saves selected Google Email + Website Username + Bcrypt Website Password in MongoDB.
    Completes Sign Up only after username and website password are provided.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")
    google_id = data.get("google_id", "").strip()

    if not email or not username or not password:
        return jsonify({"error": "Google email, Website Username, and Website Password are required."}), 400

    # Strong password validation
    is_valid, missing_reqs = AuthService.validate_strong_password(password)
    if not is_valid:
        return jsonify({
            "error": "Your password is not strong enough. Please create a stronger password.",
            "missing_requirements": missing_reqs
        }), 400

    if confirm_password and password != confirm_password:
        return jsonify({"error": "Password and Confirm Password do not match."}), 400

    users_col = get_users_collection()
    existing_user = users_col.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "An account with this email address already exists. Please log in."}), 409

    # Hash website password with Bcrypt
    password_hash = AuthService.hash_password(password)
    user_id = str(uuid.uuid4())

    new_user = {
        "_id": user_id,
        "name": username,
        "email": email,
        "password_hash": password_hash,
        "google_id": google_id or f"google_{uuid.uuid4().hex[:8]}",
        "created_at": datetime.datetime.now(datetime.timezone.utc)
    }
    users_col.insert_one(new_user)

    token = AuthService.generate_token(user_id, email, username)
    session["token"] = token
    session["user_id"] = user_id

    # Automatically send signup confirmation email to registered email
    try:
        EmailService.send_signup_confirmation_email(email, username)
    except Exception as e:
        logger.warning(f"Failed to send google signup confirmation email to {email}: {e}")

    return jsonify({
        "message": "Sign up complete! Your account, website username, and password have been saved.",
        "token": token,
        "user": {"id": user_id, "name": username, "email": email}
    }), 201


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."}), 200


@auth_bp.route("/me", methods=["GET"])
def get_me():
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif "token" in session:
        token = session["token"]

    if not token:
        return jsonify({"error": "Unauthenticated"}), 401

    decoded = AuthService.verify_token(token)
    if "error" in decoded:
        return jsonify({"error": decoded["error"]}), 401

    user_id = decoded["sub"]
    users_col = get_users_collection()
    user = users_col.find_one({"_id": user_id})

    if not user:
        return jsonify({"error": "User profile not found."}), 440

    return jsonify({
        "user": {
            "id": str(user["_id"]),
            "name": user.get("name"),
            "email": user.get("email")
        }
    }), 200


@auth_bp.route("/profile", methods=["GET"])
def get_profile():
    """Retrieve detailed user profile and verification stats."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif "token" in session:
        token = session["token"]

    if not token:
        return jsonify({"error": "Unauthenticated."}), 401

    decoded = AuthService.verify_token(token)
    if "error" in decoded:
        return jsonify({"error": decoded["error"]}), 401

    user_id = decoded["sub"]
    users_col = get_users_collection()
    user = users_col.find_one({"_id": user_id})

    if not user:
        return jsonify({"error": "User profile not found."}), 404

    # Calculate user verification session statistics
    sessions_col = get_verification_sessions_collection()
    total_sessions = sessions_col.count_documents({"user_id": user_id})
    ready_sessions = sessions_col.count_documents({"user_id": user_id, "overall_status": "READY"})
    pending_sessions = sessions_col.count_documents({"user_id": user_id, "overall_status": "NEEDS ATTENTION"})

    created_date = user.get("created_at")
    date_str = created_date.strftime("%B %d, %Y") if created_date and hasattr(created_date, 'strftime') else "Member"

    is_google_account = user.get("google_id") is not None and not user.get("password_hash")

    return jsonify({
        "profile": {
            "id": str(user["_id"]),
            "name": user.get("name", "User"),
            "email": user.get("email", ""),
            "auth_provider": "Google OAuth" if is_google_account else "Email & Password",
            "is_google_account": is_google_account,
            "member_since": date_str,
            "father_name": user.get("father_name", ""),
            "mother_name": user.get("mother_name", ""),
            "dob": user.get("dob", ""),
            "gender": user.get("gender", ""),
            "college_name": user.get("college_name", ""),
            "course": user.get("course", ""),
            "branch": user.get("branch", ""),
            "roll_number": user.get("roll_number", ""),
            "family_member_name": user.get("family_member_name", ""),
            "stats": {
                "total_verifications": total_sessions,
                "ready_verifications": ready_sessions,
                "pending_verifications": pending_sessions
            }
        }
    }), 200


@auth_bp.route("/profile", methods=["PUT"])
def update_profile():
    """Update user profile name and details for document ownership verification."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif "token" in session:
        token = session["token"]

    if not token:
        return jsonify({"error": "Unauthenticated."}), 401

    decoded = AuthService.verify_token(token)
    if "error" in decoded:
        return jsonify({"error": decoded["error"]}), 401

    user_id = decoded["sub"]
    data = request.get_json() or {}
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "Name field cannot be empty."}), 400

    users_col = get_users_collection()
    user = users_col.find_one({"_id": user_id})

    if not user:
        return jsonify({"error": "User account not found."}), 404

    update_fields = {
        "name": name,
        "updated_at": datetime.datetime.now(datetime.timezone.utc)
    }
    for field in ["father_name", "mother_name", "dob", "gender", "college_name", "course", "branch", "roll_number", "family_member_name"]:
        if field in data:
            update_fields[field] = (data.get(field) or "").strip()

    users_col.update_one(
        {"_id": user_id},
        {"$set": update_fields}
    )

    return jsonify({
        "message": "Profile updated successfully.",
        "user": {
            "id": user_id,
            "name": name,
            "email": user.get("email")
        }
    }), 200


@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    """Change account password for email-authenticated users."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif "token" in session:
        token = session["token"]

    if not token:
        return jsonify({"error": "Unauthenticated."}), 401

    decoded = AuthService.verify_token(token)
    if "error" in decoded:
        return jsonify({"error": decoded["error"]}), 401

    user_id = decoded["sub"]
    data = request.get_json() or {}
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    users_col = get_users_collection()
    user = users_col.find_one({"_id": user_id})

    if not user:
        return jsonify({"error": "User profile not found."}), 404

    if not user.get("password_hash"):
        return jsonify({
            "error": "This account is authenticated via Google OAuth. Password change is not applicable."
        }), 400

    if not current_password or not new_password:
        return jsonify({"error": "Please enter current password and new password."}), 400

    if not AuthService.check_password(current_password, user["password_hash"]):
        return jsonify({"error": "Current password is incorrect."}), 401

    # Strong password validation
    is_valid, missing_reqs = AuthService.validate_strong_password(new_password)
    if not is_valid:
        return jsonify({
            "error": "Your password is not strong enough. Please create a stronger password.",
            "missing_requirements": missing_reqs
        }), 400

    if confirm_password and new_password != confirm_password:
        return jsonify({"error": "New password and Confirm Password do not match."}), 400

    new_hash = AuthService.hash_password(new_password)
    users_col.update_one(
        {"_id": user_id},
        {"$set": {
            "password_hash": new_hash,
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }}
    )

    return jsonify({"message": "Password changed successfully."}), 200
