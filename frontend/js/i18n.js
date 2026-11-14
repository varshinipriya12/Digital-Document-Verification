// Centralized Internationalization (i18n) Module: English & Telugu (తెలుగు)

const translations = {
  en: {
    // Header & Brand
    portal_title: "🏛️ Official Public Digital Document Verification Portal",
    sub_portal: "Preliminary Application Readiness Check",
    brand_main: "DIGITAL DOC VERIFY",
    brand_sub: "Government Services Assistant",

    // Navigation
    nav_home: "Home",
    nav_services: "Services",
    nav_how_it_works: "How It Works",
    nav_my_verifications: "My Verifications",
    nav_signin: "Sign In",
    nav_signup: "Sign Up",
    nav_logout: "Logout",

    // Disclaimer
    disclaimer_label: "DISCLAIMER:",
    disclaimer_text: "This is a preliminary document-readiness check. It does not confirm legal authenticity or official government approval.",

    // Hero / Home Page
    hero_badge: "AI-Powered Verification Engine",
    hero_title: "Prepare Your Documents Before You Apply",
    hero_subtitle: "Upload your government documents and verify whether they are clear, complete, and correct before applying on official government portals.",
    btn_select_service: "Start Document Verification →",
    btn_how_it_works: "How Verification Works",
    steps_heading: "Simple 3-Step Verification Process",
    step1_title: "1. Select Document Verification",
    step1_desc: "Choose Government Document Verification to verify Aadhaar, PAN, Income, Caste, Residence, Birth Certificate, Passport, and Marksheets.",
    step2_title: "2. Upload Required Documents",
    step2_desc: "Upload Aadhaar, PAN, Income Proof, Caste Certificate, Passport, or Educational Marksheets in PDF, JPG, or PNG format.",
    step3_title: "3. Verify & Get Report",
    step3_desc: "OpenCV checks image clarity/blur, OCR extracts text, and Gemini AI verifies document-type matching before official submission.",

    // Login & Signup Forms
    login_title: "Sign In to Your Account",
    login_sub: "Access government service document verification tools",
    signup_title: "Create an Account",
    signup_sub: "Register to save and manage document verification sessions",
    btn_google: "Continue with Google",
    form_divider: "or sign in with email",
    form_divider_signup: "or sign up with email",
    lbl_name: "Full Name",
    ph_name: "Rahul Sharma",
    lbl_email: "Email Address",
    ph_email: "rahul@example.com",
    lbl_password: "Password",
    ph_password: "At least 8 characters",
    lbl_confirm_password: "Confirm Password",
    ph_confirm_password: "Repeat password",
    btn_create_account: "Create Account →",
    no_account: "Don't have an account?",
    already_account: "Already have an account?",
    forgot_password_link: "Forgot Password?",

    // Forgot Password & OTP Modal
    forgot_title: "Reset Your Password",
    forgot_sub: "Verify your email address using a 6-digit OTP code",
    btn_send_otp: "Send OTP →",
    btn_verify_otp: "Verify OTP →",
    btn_reset_password: "Reset Password →",
    lbl_otp: "6-Digit OTP Code",
    ph_otp: "123456",
    lbl_new_password: "New Password",
    ph_new_password: "At least 8 characters",

    // Services Catalog Page
    services_catalog_badge: "Document Verification System",
    services_heading: "Government Document Verification",
    services_sub: "Upload and verify various government-related documents through a single AI-powered document verification system.",
    btn_start_doc_verification: "Start Document Verification →",
    btn_select_service_card: "Start Document Verification →",

    // Government Application Portals Section
    portals_badge: "Direct Application Links",
    portals_heading: "Official Government Application Portals",
    portals_sub: "Once your documents are verified, navigate directly to official government portals to apply for services.",
    btn_visit_official_portal: "Visit Official Portal ↗",

    // Document Upload Page
    back_to_services: "← Back to Services",
    docs_req_title_prefix: "Documents Required for",
    upload_page_sub: "Upload clear copies of the required documents below. Uploading a file does not mean it is verified yet—document types will be checked during verification.",
    btn_select_upload: "📤 Select & Upload File",
    upload_formats_note: "Formats: PDF, JPG, PNG (Max 8 MB)",
    upload_status_note: "ℹ️ File uploaded. Document type will be checked during verification.",
    btn_replace: "Replace",
    btn_remove: "Remove",
    upload_ready_heading: "Ready to Verify Your Uploaded Documents?",
    upload_ready_sub: "Click below to run OpenCV quality inspection, OCR text extraction, and Gemini AI document matching.",
    btn_start_verification: "⚡ Start Document Verification →",

    // Verification & Report
    verifying_heading: "Running Document Verification",
    verifying_sub: "Initializing OpenCV Quality Inspection...",
    verifying_step1: "1. Quality & Clarity Check",
    verifying_step2: "2. OCR Readability",
    verifying_step3: "3. Document Type Verification",
    report_badge: "Verification Session Report",
    stat_total: "Total Required",
    stat_verified: "Verified",
    stat_poor_quality: "Poor Quality",
    stat_invalid_type: "Invalid Document Type",
    stat_needs_review: "Needs Review",
    stat_ready: "Verified",
    stat_needs_attention: "Needs Attention",
    stat_invalid: "Invalid Type",
    stat_missing: "Missing",
    btn_proceed_portal: "Proceed to Official Government Portal →",
    btn_action_required: "🚫 Action Required: Fix issues before proceeding to Official Portal",
    doc_results_heading: "Document-Wise Results",
    confidence_label: "Confidence:",
    extracted_text_label: "View Extracted OCR Text Snippet",
    analysis_label: "Analysis Result:",

    // Status Badges
    status_ready: "READY",
    status_needs_attention: "NEEDS ATTENTION",
    status_invalid: "INVALID",
    status_missing: "MISSING",

    // History Page
    history_badge: "Session History",
    history_title: "My Previous Verifications",
    history_sub: "Review previous document-readiness check reports and recommendations saved in your account.",
    tbl_service: "Government Service",
    tbl_date: "Date & Time",
    tbl_required: "Required Docs",
    tbl_status: "Overall Status",
    tbl_action: "Action",
    btn_view_report: "View Report →",
    no_history_title: "No Previous Verifications Found",
    no_history_sub: "You have not verified any government service documents yet.",

    // How It Works Page
    how_badge: "System Architecture & Workflow",
    how_title: "How Verification Works",
    how_sub: "Understand how OpenCV image processing, Tesseract OCR, and Google Gemini AI work together to ensure your documents are ready before submission.",
    how_step1_t: "1. Create an Account or Sign In",
    how_step1_d: "Sign in using email credentials or Google OAuth to secure your verification sessions.",
    how_step2_t: "2. Select Government Document Verification",
    how_step2_d: "Select the unified Government Document Verification service supporting Aadhaar, PAN, Income, Caste, Residence, Birth Certificate, Passport, and Marksheets.",
    how_step3_t: "3. View Required Documents",
    how_step3_d: "Dynamically fetch official document requirements stored in MongoDB.",
    how_step4_t: "4. Upload Documents",
    how_step4_d: "Upload PDF, JPG, or PNG files (up to 8 MB per file). Files are securely stored with random UUIDs.",
    how_step5_t: "5. OpenCV Document Quality Inspection",
    how_step5_d: "OpenCV calculates Laplacian variance for blur detection, mean brightness, resolution, and blank image checks.",
    how_step6_t: "6. OCR Text Extraction",
    how_step6_d: "PyTesseract performs image thresholding and extracts readable text snippets for evidence matching.",
    how_step7_t: "7. Gemini AI Document-Type & Content Verification",
    how_step7_d: "Google Gemini AI checks whether the uploaded file actually matches the required document type (e.g. flagging an Aadhaar card uploaded into an Income Proof slot as INVALID).",
    how_step8_t: "8. Receive Document-Wise Results",
    how_step8_d: "Get itemized status badges (READY, NEEDS ATTENTION, INVALID, MISSING) with confidence scores.",
    how_step9_t: "9. Review Final Verification Report",
    how_step9_d: "Inspect overall session status and actionable recommendations if any document needs attention.",
    how_step10_t: "10. Continue to Official Government Portal",
    how_step10_d: "Once all documents pass as READY, click through to the official portal to complete your official application.",

    // Footer
    footer_title: "Digital Document Verification Assistant",
    footer_sub: "Preliminary Document-Readiness Tool for Government Applications"
  },

  te: {
    // Header & Brand (Telugu)
    portal_title: "🏛️ అధికారిక ప్రజా డిజిటల్ పత్రాల పరిశీలన పోర్టల్",
    sub_portal: "ప్రాథమిక దరఖాస్తు సిద్ధత తనిఖీ",
    brand_main: "డిజిటల్ పత్రాల తనిఖీ",
    brand_sub: "ప్రభుత్వ సేవల సహాయకుడే",

    // Navigation
    nav_home: "హోమ్",
    nav_services: "ప్రభుత్వ సేవలు",
    nav_how_it_works: "ఎలా పనిచేస్తుంది",
    nav_my_verifications: "నా పరిశీలనలు",
    nav_signin: "సైన్ ఇన్",
    nav_signup: "సైన్ అప్",
    nav_logout: "లాగ్ అవుట్",

    // Disclaimer
    disclaimer_label: "గమనిక:",
    disclaimer_text: "ఇది ప్రాథమిక పత్రాల తనిఖీ మాత్రమే. ఇది చట్టపరమైన ప్రామాణికత లేదా అధికారిక ప్రభుత్వ ఆమోదాన్ని నిర్ధారించదు.",

    // Hero / Home Page
    hero_badge: "ఏఐ-ఆధారిత పరిశీలన ఇంజిన్",
    hero_title: "మీరు దరఖాస్తు చేసే ముందు మీ పత్రాలను సిద్ధం చేసుకోండి",
    hero_subtitle: "మీ ప్రభుత్వ పత్రాలను అప్‌లోడ్ చేసి, అధికారిక పోర్టల్‌లలో దరఖాస్తు చేయడానికి ముందు అవి స్పష్టంగా, సంపూర్ణంగా ఉన్నాయో లేదో ధృవీకరించండి.",
    btn_select_service: "పత్రాల పరిశీలన ప్రారంభించండి →",
    btn_how_it_works: "పరిశీలన ఎలా పనిచేస్తుంది",
    steps_heading: "సులువైన 3-దశల పరిశీలన ప్రక్రియ",
    step1_title: "1. పత్రాల పరిశీలనను ఎంచుకోండి",
    step1_desc: "ఆధార్, పాన్, ఆదాయం, కులం, నివాసం, జనన ధృవీకరణ పత్రం, పాస్‌పోర్ట్ మరియు మార్క్‌షీట్‌లను ధృవీకరించడానికి ప్రభుత్వ పత్రాల పరిశీలనను ఎంచుకోండి.",
    step2_title: "2. అవసరమైన పత్రాలను అప్‌లోడ్ చేయండి",
    step2_desc: "ఆధార్, పాన్, ఆదాయం, కుల పత్రం, పాస్‌పోర్ట్ లేదా మార్కుల జాబితాను PDF, JPG, లేదా PNG రూపంలో అప్‌లోడ్ చేయండి.",
    step3_title: "3. పరిశీలించి నివేదిక పొందండి",
    step3_desc: "అధికారిక సమర్పణకు ముందు OpenCV నాణ్యతను తనిఖీ చేస్తుంది, OCR వచనాన్ని సంగ్రహిస్తుంది, మరియు జెమిని AI పత్రం రకాన్ని సరిపోలుస్తుంది.",

    // Login & Signup Forms
    login_title: "మీ ఖాతాకు సైన్ ఇన్ చేయండి",
    login_sub: "ప్రభుత్వ సేవల పత్రాల పరిశీలన సాధనాలను పొందండి",
    signup_title: "ఖాతాను సృష్టించండి",
    signup_sub: "పరిశీలన సెషన్‌లను సేవ్ చేయడానికి నమోదు చేసుకోండి",
    btn_google: "గూగుల్‌తో కొనసాగించండి",
    form_divider: "లేదా ఈమెయిల్‌తో సైన్ ఇన్ చేయండి",
    form_divider_signup: "లేదా ఈమెయిల్‌తో సైన్ అప్ చేయండి",
    lbl_name: "పూర్తి పేరు",
    ph_name: "రాహుల్ శర్మ",
    lbl_email: "ఈమెయిల్ విలాసం",
    ph_email: "rahul@example.com",
    lbl_password: "పాస్‌వర్డ్",
    ph_password: "కనీసం 6 అక్షరాలు",
    lbl_confirm_password: "పాస్‌వర్డ్ నిర్ధారించండి",
    ph_confirm_password: "పాస్‌వర్డ్‌ను మళ్లీ నమోదు చేయండి",
    btn_create_account: "ఖాతాను సృష్టించండి →",
    no_account: "ఖాతా లేదా?",
    already_account: "ఇప్పటికే ఖాతా ఉందా?",
    forgot_password_link: "పాస్‌వర్డ్ మరిచిపోయారా?",

    // Forgot Password & OTP Modal
    forgot_title: "పాస్‌వర్డ్‌ను రీసెట్ చేయండి",
    forgot_sub: "6-అంకెల OTP కోడ్‌ను ఉపయోగించి మీ ఈమెయిల్‌ను ధృవీకరించండి",
    btn_send_otp: "OTP పంపండి →",
    btn_verify_otp: "OTP ధృవీకరించండి →",
    btn_reset_password: "పాస్‌వర్డ్ రీసెట్ చేయండి →",
    lbl_otp: "6-అంకెల OTP కోడ్",
    ph_otp: "123456",
    lbl_new_password: "కొత్త పాస్‌వర్డ్",
    ph_new_password: "కనీసం 6 అక్షరాలు",

    // Services Catalog Page
    services_catalog_badge: "పత్రాల పరిశీలన వ్యవస్థ",
    services_heading: "ప్రభుత్వ పత్రాల పరిశీలన",
    services_sub: "ఏకీకృత AI ఆధారిత పత్రాల పరిశీలన వ్యవస్థ ద్వారా వివిధ ప్రభుత్వ సంబంధిత పత్రాలను అప్‌లోడ్ చేసి పరిశీలించండి.",
    btn_start_doc_verification: "పత్రాల పరిశీలన ప్రారంభించండి →",
    btn_select_service_card: "పత్రాల పరిశీలన ప్రారంభించండి →",

    // Government Application Portals Section
    portals_badge: "ప్రత్యక్ష దరఖాస్తు లింకులు",
    portals_heading: "అధికారిక ప్రభుత్వ దరఖాస్తు పోర్టల్‌లు",
    portals_sub: "మీ పత్రాలు సరిచూడబడిన తర్వాత సేవల కోసం దరఖాస్తు చేసుకోవడానికి అధికారిక ప్రభుత్వ పోర్టల్‌లను సందర్శించండి.",
    btn_visit_official_portal: "అధికారిక పోర్టల్‌ను సందర్శించండి ↗",

    // Document Upload Page
    back_to_services: "← సేవలకు తిరిగి వెళ్లండి",
    docs_req_title_prefix: "అవసరమైన పత్రాలు:",
    upload_page_sub: "అవసరమైన పత్రాల స్పష్టమైన ప్రతులను క్రింద అప్‌లోడ్ చేయండి. అప్‌లోడ్ చేయడం మాత్రమే పరిశీలన పూర్తయినట్లు కాదు—పరిశీలన సమయంలో పత్రం రకం తనిఖీ చేయబడుతుంది.",
    btn_select_upload: "📤 ఫైల్‌ను ఎంచుకుని అప్‌లోడ్ చేయండి",
    upload_formats_note: "ఫార్మాట్‌లు: PDF, JPG, PNG (గరిష్టం 8 MB)",
    upload_status_note: "ℹ️ ఫైల్ అప్‌లోడ్ చేయబడింది. పరిశీలన సమయంలో పత్రం రకం తనిఖీ చేయబడుతుంది.",
    btn_replace: "మార్చండి",
    btn_remove: "తొలగించండి",
    upload_ready_heading: "అప్‌లోడ్ చేసిన పత్రాలను పరిశీలించడానికి సిద్ధంగా ఉన్నారా?",
    upload_ready_sub: "OpenCV నాణ్యత తనిఖీ, OCR వచన సేకరణ, మరియు జెమిని AI పోలిక ప్రక్రియ ప్రారంభించడానికి క్రింద క్లిక్ చేయండి.",
    btn_start_verification: "⚡ పత్రాల పరిశీలన ప్రారంభించండి →",

    // Verification & Report
    verifying_heading: "పత్రాల పరిశీలన జరుగుతోంది",
    verifying_sub: "OpenCV నాణ్యత తనిఖీ ప్రారంభమవుతోంది...",
    verifying_step1: "1. నాణ్యత & స్పష్టత తనిఖీ",
    verifying_step2: "2. OCR వచన రీడబిలిటీ",
    verifying_step3: "3. పత్రం రకం ధృవీకరణ",
    report_badge: "పరిశీలన సెషన్ నివేదిక",
    stat_total: "మొత్తం అవసరమైనవి",
    stat_verified: "ధృవీకరించబడింది",
    stat_poor_quality: "నాణ్యత లోపం",
    stat_invalid_type: "తప్పుడు పత్రం",
    stat_needs_review: "సమీక్ష అవసరం",
    stat_ready: "ధృవీకరించబడింది",
    stat_needs_attention: "గమనించాలి",
    stat_invalid: "తప్పుడు పత్రం",
    stat_missing: "లభ్యం కాలేదు",
    btn_proceed_portal: "అధికారిక ప్రభుత్వ పోర్టల్‌కు వెళ్లండి →",
    btn_action_required: "🚫 చర్య అవసరం: పోర్టల్‌కు వెళ్ళే ముందు సమస్యలను సరిచేయండి",
    doc_results_heading: "పత్రాల వారీగా ఫలితాలు",
    confidence_label: "నమ్మకం స్థాయి:",
    extracted_text_label: "సేకరించిన OCR వచనాన్ని చూడండి",
    analysis_label: "విశ్లేషణ ఫలితం:",

    // Status Badges
    status_ready: "సిద్ధంగా ఉంది (READY)",
    status_needs_attention: "గమనించాలి (NEEDS ATTENTION)",
    status_invalid: "చెల్లదు (INVALID)",
    status_missing: "లభ్యం కాలేదు (MISSING)",

    // History Page
    history_badge: "సెషన్ చరిత్ర",
    history_title: "నా మునుపటి పరిశీలనలు",
    history_sub: "మీ ఖాతాలో సేవ్ చేయబడిన పత్రాల తనిఖీ నివేదికలు మరియు సూచనలను సమీక్షించండి.",
    tbl_service: "ప్రభుత్వ సేవ",
    tbl_date: "తేదీ & సమయం",
    tbl_required: "అవసరమైన పత్రాలు",
    tbl_status: "మొత్తం స్థితి",
    tbl_action: "చర్య",
    btn_view_report: "నివేదిక చూడండి →",
    no_history_title: "మునుపటి పరిశీలనలు ఏవీ కనుగొనబడలేదు",
    no_history_sub: "మీరు ఇప్పటివరకు ఏ ప్రభుత్వ సేవ పత్రాలను పరిశీలించలేదు.",

    // How It Works Page
    how_badge: "సిస్టమ్ నిర్మాణం మరియు విధానం",
    how_title: "పరిశీలన ఎలా పనిచేస్తుంది",
    how_sub: "సమర్పణకు ముందు మీ పత్రాలు సిద్ధంగా ఉన్నాయని నిర్ధారించుకోవడానికి OpenCV ఇమేజ్ ప్రాసెసింగ్, టెస్సరాక్ట్ OCR మరియు గూగుల్ జెమిని AI కలిసి ఎలా పనిచేస్తాయో అర్థం చేసుకోండి.",
    how_step1_t: "1. ఖాతాను సృష్టించండి లేదా సైన్ ఇన్ చేయండి",
    how_step1_d: "మీ పరిశీలన సెషన్‌లను భద్రపరచడానికి ఈమెయిల్ ఆధారాలు లేదా గూగుల్ ఆధారాలతో సైన్ ఇన్ చేయండి.",
    how_step2_t: "2. ప్రభుత్వ పత్రాల పరిశీలనను ఎంచుకోండి",
    how_step2_d: "ఆధార్, పాన్, ఆదాయం, కులం, నివాసం, జనన ధృవీకరణ పత్రం, పాస్‌పోర్ట్ మరియు మార్క్‌షీట్‌లకు మద్దతు ఇచ్చే ఏకీకృత ప్రభుత్వ పత్రాల పరిశీలన సేవను ఎంచుకోండి.",
    how_step3_t: "3. అవసరమైన పత్రాలను చూడండి",
    how_step3_d: "మొంగోడిబి లో నిల్వ చేయబడిన అధికారిక పత్రాల అవసరాలను పొందండి.",
    how_step4_t: "4. పత్రాలను అప్‌లోడ్ చేయండి",
    how_step4_d: "PDF, JPG లేదా PNG ఫైళ్లను అప్‌లోడ్ చేయండి (ఫైల్‌కు గరిష్టంగా 8 MB). ఫైళ్లు భద్రంగా నిల్వ చేయబడతాయి.",
    how_step5_t: "5. OpenCV పత్ర నాణ్యత తనిఖీ",
    how_step5_d: "OpenCV మసకబారడం, ప్రకాశం, రిజల్యూషన్ మరియు ఖాళీ పేజీ తనిఖీలను లెక్కిస్తుంది.",
    how_step6_t: "6. OCR వచన సేకరణ",
    how_step6_d: "PyTesseract ఇమేజ్ థ్రెషోల్డింగ్ చేసి పత్రంలోని చదవగలిగే వచనాన్ని సంగ్రహిస్తుంది.",
    how_step7_t: "7. జెమిని AI పత్ర రకం మరియు విషయ పరిశీలన",
    how_step7_d: "అప్‌లోడ్ చేసిన ఫైల్ నిజంగా అవసరమైన పత్రం రకానికి సరిపోలుతుందో లేదో గూగుల్ జెమిని AI తనిఖీ చేస్తుంది (ఉదా. ఆదాయ రుజువు స్థానంలో అప్‌లోడ్ చేసిన ఆధార్ కార్డ్‌ను 'చెల్లదు' అని గుర్తుస్తుంది).",
    how_step8_t: "8. పత్రాల వారీగా ఫలితాలు పొందండి",
    how_step8_d: "నమ్మకం స్థాయులతో ఐటమైజ్ చేసిన స్థితి బ్యాడ్జ్‌లను పొందండి.",
    how_step9_t: "9. అంతిమ పరిశీలన నివేదికను సమీక్షించండి",
    how_step9_d: "మొత్తం సెషన్ స్థితిని మరియు ఏదైనా పత్రానికి గమనింపు అవసరమైతే చర్యలను తనిఖీ చేయండి.",
    how_step10_t: "10. అధికారిక ప్రభుత్వ పోర్టల్‌కు వెళ్లండి",
    how_step10_d: "అన్ని పత్రాలు 'సిద్ధంగా ఉన్నాయి' అని ఆమోదించబడిన తర్వాత, దరఖాస్తు పూర్తి చేయడానికి అధికారిక పోర్టల్‌కు వెళ్లండి.",

    // Footer
    footer_title: "డిజిటల్ పత్రాల పరిశీలన సహాయకుడు",
    footer_sub: "ప్రభుత్వ దరఖాస్తుల కోసం ప్రాథమిక పత్రాల సిద్ధత సాధనం"
  }
};

// Current language getter & setter (Persisted in localStorage)
function getLanguage() {
  return localStorage.getItem("app_lang") || "en";
}

function setLanguage(lang) {
  if (lang !== "en" && lang !== "te") lang = "en";
  localStorage.setItem("app_lang", lang);
  updatePageLanguage();

  // Trigger dynamic page re-renders if the active page has a dynamic loader
  if (typeof loadGovernmentServices === 'function' && document.getElementById("services-grid-container")) {
    loadGovernmentServices();
  }
  if (typeof initAuthNavbar === 'function' && document.getElementById("nav-auth-container")) {
    initAuthNavbar();
  }
  if (typeof loadVerificationHistory === 'function' && document.getElementById("history-container")) {
    loadVerificationHistory();
  }
}

function t(key) {
  const lang = getLanguage();
  return (translations[lang] && translations[lang][key]) || translations.en[key] || key;
}

function updatePageLanguage() {
  const lang = getLanguage();

  // Update text content for data-i18n
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (key && translations[lang] && translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });

  // Update input placeholders for data-i18n-placeholder
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (key && translations[lang] && translations[lang][key]) {
      el.placeholder = translations[lang][key];
    }
  });

  // Update language selector dropdown if present
  const langSelect = document.getElementById("lang-select");
  if (langSelect) {
    langSelect.value = lang;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  updatePageLanguage();
});
