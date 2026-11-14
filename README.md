# Digital Document Verification for Government Services

A preliminary document-readiness and verification assistant for government-service applications. This full-stack web application enables users to select a government service, view required documents dynamically from MongoDB, upload copies, and run automated OpenCV quality checks (blur, brightness, resolution), Tesseract OCR text extraction, and Google Gemini AI multimodal verification to ensure uploaded documents match the required document types before applying on official government portals.

> **IMPORTANT DISCLAIMER:**
> This application is a preliminary document-readiness check. It does not confirm legal authenticity or official government approval.

---

## Technology Stack

- **Frontend**: HTML5, CSS3 (Luxury Government Portal Theme with Warm Ivory `#F9F8F3`, Dark Navy `#0F172A`, Saffron `#D97706`), Vanilla JavaScript (ES6+ REST API client)
- **Backend**: Python 3.13+, Flask REST API, Flask-CORS
- **Database**: MongoDB (with MongoDB client connection & automated `mongomock` in-memory database fallback)
- **Document Processing**: OpenCV (`cv2`), PyTesseract OCR, Pillow, PyPDF
- **AI Verification**: Google Gemini API (`google-genai` SDK)
- **Authentication**: Email/Password authentication with `bcrypt` password hashing, JWT session tokens, Google OAuth integration

---

## Project Directory Structure

```
digital_doc_verification/
├── backend/
│   ├── app.py                     # Flask application entry point
│   ├── config.py                  # App configuration & environment constants
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Secrets & environment configuration
│   ├── .env.example               # Template environment configuration
│   ├── database/
│   │   ├── mongodb.py             # MongoDB client connection & mongomock fallback
│   │   └── seed.py                # Database seeder for government services & requirements
│   ├── services/
│   │   ├── auth_service.py        # Password hashing with bcrypt, JWT & Google OAuth
│   │   ├── opencv_service.py      # OpenCV blur (Laplacian var), brightness & resolution check
│   │   ├── ocr_service.py         # PyTesseract OCR text extraction
│   │   └── gemini_service.py      # Google Gemini AI document verification
│   ├── routes/
│   │   ├── auth.py                # Signup, login, logout, me & Google OAuth APIs
│   │   ├── services.py            # Services & requirements REST APIs
│   │   ├── uploads.py             # File upload handler (max 8MB, PDF/JPG/PNG)
│   │   └── verification.py       # Verification pipeline runner & report retrieval
│   └── uploads/                   # Secure UUID file storage directory
├── frontend/
│   ├── index.html                 # Landing page & hero dashboard
│   ├── login.html                 # Login page with Google Sign-In button
│   ├── signup.html                # Account creation page with validation
│   ├── dashboard.html             # User portal dashboard
│   ├── services.html              # Government service selection cards
│   ├── documents.html             # Document upload page
│   ├── verification.html          # Verification progress & document-wise results
│   ├── report.html                # Final verification report & official portal CTA
│   ├── my-verifications.html      # History of verification sessions
│   ├── how-it-works.html          # 10-step detailed explanation & disclaimer
│   ├── css/
│   │   └── style.css              # Custom government portal styling system
│   └── js/
│       ├── config.js              # REST API base URL & session state
│       ├── auth.js                # Auth state management
│       ├── services.js            # Dynamic services renderer
│       ├── uploads.js             # Drag & drop upload & validation
│       ├── verification.js       # Verification pipeline renderer
│       └── history.js             # Verification history loader
└── README.md                      # Windows setup & test case guide
```

---

## Environment Setup Instructions (Windows)

### Step 1: Open PowerShell or Command Prompt
Navigate to the project root directory:
```powershell
cd C:\Users\Varshini\.gemini\antigravity\scratch\digital_doc_verification
```

### Step 2: Create & Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
```

### Step 3: Install Python Dependencies
```powershell
.\venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

### Step 4: Configure Environment Variables (`backend/.env`)
Edit `backend/.env` to configure your keys:
```env
SECRET_KEY=dev-secret-key-gov-doc-verification-2026
JWT_SECRET_KEY=dev-jwt-secret-key-gov-doc-verification-2026

# MongoDB URI (Falls back to mongomock if local MongoDB is offline)
MONGODB_URI=mongodb://localhost:27017/gov_doc_verification
DB_NAME=gov_doc_verification

# Google Gemini API key (Get from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here

# Google OAuth Credentials (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Step 5: Seed MongoDB Database
Populate the 5 default government services (Income Certificate, Caste Certificate, Residence Certificate, Scholarship Application, Birth Certificate) and document requirements:
```powershell
.\venv\Scripts\python.exe backend/database/seed.py
```

---

## Running the Application Locally

Start the Flask Backend Server:
```powershell
.\venv\Scripts\python.exe backend/app.py
```
*The server will start on **`http://localhost:5000`** and serve both the REST API endpoints and the frontend UI.*

Open your web browser and navigate to:
```
http://localhost:5000
```

---

## Executing Document Verification Test Cases

| Test Case | Required Document | Uploaded File | Expected Result | Result Status |
|---|---|---|---|---|
| **TEST 1** | Aadhaar Card | Aadhaar Card (Clear image/PDF) | Document matches required type and is clear. | `READY` |
| **TEST 2** | Income Proof | Aadhaar Card | Document mismatched. Detected Aadhaar instead of Income Proof. | `INVALID` |
| **TEST 3** | Address Proof | Extremely Blurry / Out of Focus Image | OpenCV Laplacian variance identifies blur. | `NEEDS ATTENTION` |
| **TEST 4** | Income Proof | Valid Income Certificate / Salary Slip | Document type and readability confirmed. | `READY` |
| **TEST 5** | Marksheet | *(None uploaded)* | Required document slot left empty. | `MISSING` |
| **TEST 6** | Aadhaar Card | `document.exe` or `test.txt` | Upload rejected by MIME/extension validator. | `Upload Rejected (400)` |
| **TEST 7** | Income Proof | File > 8.0 MB | Upload rejected by file size validator. | `Upload Rejected (413)` |
| **TEST 8** | Any Document | *(GEMINI_API_KEY omitted)* | Safe fallback with backend error logging. | `NEEDS ATTENTION` |
