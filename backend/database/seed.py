import sys
import os
import datetime

# Ensure utf-8 stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to sys.path to resolve config & mongodb imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.mongodb import (
    get_services_collection,
    get_documents_collection,
    get_service_documents_collection,
    get_users_collection
)

def seed_database():
    services_col = get_services_collection()
    documents_col = get_documents_collection()
    service_docs_col = get_service_documents_collection()

    # Clear existing sample data for clean re-seeding
    services_col.delete_many({})
    documents_col.delete_many({})
    service_docs_col.delete_many({})

    print("Seeding Document Definitions...")
    documents = [
        # --- 18 Approved Core Documents ---
        {
            "_id": "doc_aadhaar",
            "name": "Aadhaar Card",
            "name_te": "ఆధార్ కార్డ్",
            "slug": "aadhaar-card",
            "doc_type": "aadhaar_card",
            "icon": "🆔",
            "description": "Government of India Unique Identification Card containing 12-digit Aadhaar number issued by UIDAI.",
            "description_te": "UIDAI జారీ చేసిన 12 అంకెల ఆధార్ సంఖ్య కలిగిన భారత ప్రభుత్వ ప్రత్యేక గుర్తింపు కార్డు.",
            "expected_keywords": ["aadhaar", "unique identification", "uidai", "government of india", "dob", "male", "female", "enrollment"]
        },
        {
            "_id": "doc_pan",
            "name": "PAN Card",
            "name_te": "పాన్ కార్డ్",
            "slug": "pan-card",
            "doc_type": "pan_card",
            "icon": "💳",
            "description": "Permanent Account Number Card issued by Income Tax Department, Government of India.",
            "description_te": "భారత ప్రభుత్వ ఆదాయ పన్ను శాఖ జారీ చేసిన శాశ్వత ఖాతా సంఖ్య (PAN) కార్డు.",
            "expected_keywords": ["income tax department", "permanent account number", "pan", "govt of india", "father's name", "dob"]
        },
        {
            "_id": "doc_voter_id",
            "name": "Voter ID Card",
            "name_te": "ఓటరు గుర్తింపు కార్డ్",
            "slug": "voter-id-card",
            "doc_type": "voter_id",
            "icon": "🗳️",
            "description": "Electoral Photo Identity Card (EPIC) issued by Election Commission of India.",
            "description_te": "భారత ఎన్నికల సంఘం జారీ చేసిన ఓటరు ఫోటో గుర్తింపు కార్డు (EPIC).",
            "expected_keywords": ["election commission of india", "electoral photo identity card", "epic", "voter id", "elector", "identity card"]
        },
        {
            "_id": "doc_caste_cert",
            "name": "Caste Certificate",
            "name_te": "కుల ధృవీకరణ పత్రం",
            "slug": "caste-certificate-doc",
            "doc_type": "caste_proof",
            "icon": "📜",
            "description": "Community / Caste / Tribe Certificate issued by Revenue Department Tahsildar.",
            "description_te": "రెవెన్యూ శాఖ తహశీల్దార్ జారీ చేసిన కుల / కమ్యూనిటీ ధృవీకరణ పత్రం.",
            "expected_keywords": ["caste certificate", "community certificate", "caste", "scheduled caste", "scheduled tribe", "backward class", "tahsildar"]
        },
        {
            "_id": "doc_income_cert",
            "name": "Income Certificate",
            "name_te": "ఆదాయ ధృవీకరణ పత్రం",
            "slug": "income-certificate-doc",
            "doc_type": "income_proof",
            "icon": "📄",
            "description": "Official Income Certificate issued by Revenue Department Tahsildar, Salary Certificate, or Form 16.",
            "description_te": "రెవెన్యూ శాఖ తహశీల్దార్ జారీ చేసిన అధికారిక ఆదాయ ధృవీకరణ పత్రం, వేతన పత్రం, లేదా ఫారమ్ 16.",
            "expected_keywords": ["income certificate", "salary", "form 16", "employer", "annual income", "gross", "tahsildar", "revenue"]
        },
        {
            "_id": "doc_bank_passbook",
            "name": "Bank Passbook",
            "name_te": "బ్యాంక్ పాస్‌బుక్",
            "slug": "bank-passbook",
            "doc_type": "bank_passbook",
            "icon": "🏦",
            "description": "First page of Bank Passbook showing Account Number, Account Holder Name, IFSC code, and Branch stamp.",
            "description_te": "ఖాతా సంఖ్య మరియు IFSC కోడ్ కలిగిన బ్యాంక్ పాస్‌బుక్ మొదటి పేజీ.",
            "expected_keywords": ["bank", "account number", "account no", "ifsc", "branch", "passbook", "savings"]
        },
        {
            "_id": "doc_passport_photo",
            "name": "Passport Size Photo",
            "name_te": "పాస్‌పోర్ట్ సైజ్ ఫోటో",
            "slug": "passport-size-photo",
            "doc_type": "passport_photo",
            "icon": "📷",
            "description": "Recent color front-facing passport size portrait photograph of applicant.",
            "description_te": "దరఖాస్తుదారుడి ఇటీవలి రంగు పాస్‌పోర్ట్ సైజు ముఖచిత్ర ఫోటోగ్రాఫ్.",
            "expected_keywords": ["photo", "photograph", "passport size", "portrait"]
        },
        {
            "_id": "doc_ration_card",
            "name": "Ration Card",
            "name_te": "రేషన్ కార్డ్",
            "slug": "ration-card-doc",
            "doc_type": "ration_card",
            "icon": "🍚",
            "description": "Department of Food & Civil Supplies Ration Card or Rice Card.",
            "description_te": "పౌర సరఫరాల శాఖ రేషన్ కార్డు లేదా బియ్యం కార్డు.",
            "expected_keywords": ["ration card", "civil supplies", "food", "rice card", "consumer", "household", "fair price", "fps", "bpl", "white card"]
        },
        {
            "_id": "doc_study_cert",
            "name": "Study and Conduct Certificate",
            "name_te": "స్టడీ మరియు కాండక్ట్ సర్టిఫికేట్",
            "slug": "study-conduct-certificate",
            "doc_type": "study_certificate",
            "icon": "🎓",
            "description": "10th Study and Conduct Certificate or Intermediate Study and Conduct Certificate.",
            "description_te": "10వ తరగతి లేదా ఇంటర్మీడియట్ స్టడీ మరియు కాండక్ట్ సర్టిఫికేట్.",
            "expected_keywords": ["study and conduct certificate", "study & conduct certificate", "study certificate", "conduct certificate", "bonafide certificate", "bonafide", "school", "junior college", "conduct", "student", "admission no", "class 10th", "intermediate", "academic year"]
        },
        {
            "_id": "doc_tenth_memo",
            "name": "10th Marks Memo",
            "name_te": "10వ తరగతి మార్కుల మెమో (SSC)",
            "slug": "tenth-marks-memo",
            "doc_type": "tenth_memo",
            "icon": "📋",
            "description": "Secondary School Certificate (SSC) / 10th Class Examination Marks Sheet / DOB Extract / Transfer Certificate.",
            "description_te": "సెకండరీ స్కూల్ సర్టిఫికేట్ (SSC) / 10వ తరగతి మార్కుల మెమో.",
            "expected_keywords": ["secondary school certificate", "ssc", "board of secondary education", "10th class", "roll no", "hall ticket", "grade points", "gpa", "marks memo"]
        },
        {
            "_id": "doc_inter_memo",
            "name": "Intermediate Marks Memo",
            "name_te": "ఇంటర్మీడియట్ మార్కుల మెమో (+2)",
            "slug": "intermediate-marks-memo",
            "doc_type": "intermediate_memo",
            "icon": "📊",
            "description": "Board of Intermediate Education / Higher Secondary (10+2) Examination Marks Memorandum.",
            "description_te": "బోర్డ్ ఆఫ్ ఇంటర్మీడియట్ ఎడ్యుకేషన్ / హయ్యర్ సెకండరీ (10+2) మార్కుల మెమో.",
            "expected_keywords": ["board of intermediate education", "intermediate", "higher secondary", "10+2", "marks memo", "junior college", "total marks", "grade", "pass certificate"]
        },
        {
            "_id": "doc_father_aadhaar",
            "name": "Father's Aadhaar Card",
            "name_te": "తండ్రి ఆధార్ కార్డ్",
            "slug": "father-aadhaar-card",
            "doc_type": "father_aadhaar",
            "icon": "👨",
            "description": "Unique Identification (Aadhaar) Card of Father issued by UIDAI.",
            "description_te": "UIDAI జారీ చేసిన తండ్రి యొక్క ఆధార్ కార్డు.",
            "expected_keywords": ["aadhaar", "unique identification", "uidai", "government of india", "father"]
        },
        {
            "_id": "doc_mother_aadhaar",
            "name": "Mother's Aadhaar Card",
            "name_te": "తల్లి ఆధార్ కార్డ్",
            "slug": "mother-aadhaar-card",
            "doc_type": "mother_aadhaar",
            "icon": "👩",
            "description": "Unique Identification (Aadhaar) Card of Mother issued by UIDAI.",
            "description_te": "UIDAI జారీ చేసిన తల్లి యొక్క ఆధార్ కార్డు.",
            "expected_keywords": ["aadhaar", "unique identification", "uidai", "government of india", "mother", "female"]
        },
        {
            "_id": "doc_birth_cert",
            "name": "Birth Certificate",
            "name_te": "జనన ధృవీకరణ పత్రం",
            "slug": "birth-certificate-doc",
            "doc_type": "birth_proof",
            "icon": "👶",
            "description": "Official Birth Certificate issued by Municipal Corporation, Gram Panchayat, Registrar of Births, or Hospital / Age Proof.",
            "description_te": "మున్సిపల్ కార్పొరేషన్ లేదా జనన రిజిస్ట్రార్ జారీ చేసిన జనన ధృవీకరణ పత్రం.",
            "expected_keywords": ["birth certificate", "registrar of births and deaths", "date of birth", "place of birth", "child name", "hospital", "gram panchayat", "municipal"]
        },
        {
            "_id": "doc_college_allotment",
            "name": "College Admission / Allotment Order",
            "name_te": "కళాశాల ప్రవేశం / అలాట్‌మెంట్ ఆర్డర్",
            "slug": "college-allotment-order",
            "doc_type": "college_allotment",
            "icon": "🏛️",
            "description": "Official College Seat Allotment Order, Admission Letter, or Joining Report issued by Convener / University.",
            "description_te": "కన్వీనర్ లేదా విశ్వవిద్యాలయం జారీ చేసిన అధికారిక కళాశాల సీటు అలాట్‌మెంట్ ఆర్డర్ లేదా అడ్మిషన్ లెటర్.",
            "expected_keywords": ["allotment order", "seat allotment", "convener", "admission letter", "joining report", "college code", "branch", "course", "tuition fee", "rank", "hall ticket"]
        },
        {
            "_id": "doc_salary_slip",
            "name": "Income Proof ( Salary Slip )",
            "name_te": "ఆదాయ రుజువు (జీతపు స్లిప్ / శాలరీ స్లిప్)",
            "slug": "salary-slip",
            "doc_type": "salary_slip",
            "icon": "💵",
            "description": "Official Employer Salary Slip / Pay Slip, Salary Certificate, Form 16, or IT Returns showing earnings.",
            "description_te": "ఉద్యోగి నెలవారీ వేతనం, స్థూల ఆదాయం మరియు తగ్గింపులను చూపే అధికారిక పే స్లిప్ లేదా ఐటీ రిటర్న్స్.",
            "expected_keywords": ["salary slip", "payslip", "pay slip", "gross salary", "net pay", "basic pay", "da", "hra", "deductions", "provident fund", "employer", "employee name", "earnings", "it return", "form 16"]
        },
        {
            "_id": "doc_family_caste_cert",
            "name": "Family Member's Previously Issued Caste Certificate",
            "name_te": "కుటుంబ సభ్యుల మునుపటి కుల ధృవీకరణ పత్రం",
            "slug": "family-caste-certificate",
            "doc_type": "family_caste_proof",
            "icon": "📜",
            "description": "Previously issued Government Caste / Community Certificate of Father, Mother, Brother, or Sister issued by Revenue Authority.",
            "description_te": "తండ్రి, తల్లి, సోదరుడు లేదా సోదరి పేరుతో రెవెన్యూ అధికారి జారీ చేసిన మునుపటి కుల ధృవీకరణ పత్రం.",
            "expected_keywords": ["caste certificate", "community certificate", "father", "mother", "brother", "sister", "tahsildar", "scheduled caste", "scheduled tribe", "backward class", "revenue department", "blood relative"]
        },
        {
            "_id": "doc_address_proof",
            "name": "Address Proof",
            "name_te": "చిరునామా రుజువు",
            "slug": "address-proof",
            "doc_type": "address_proof",
            "icon": "🏠",
            "description": "Valid address proof: Ration Card / Voter ID / Aadhaar Card / House Tax Receipt / Telephone Bill / Electricity Bill.",
            "description_te": "చెల్లుబాటు అయ్యే చిరునామా రుజువు: రేషన్ కార్డ్ / ఓటరు ఐడి / ఆధార్ కార్డ్ / ఇంటి పన్ను రసీదు / టెలిఫోన్ బిల్లు / విద్యుత్ బిల్లు.",
            "expected_keywords": ["address", "ration card", "voter id", "aadhaar", "uidai", "epic", "house tax", "property tax", "telephone bill", "electricity bill", "power distribution", "consumer no", "door no", "resident", "electricity"]
        },

        # --- Specific Additional Documents for Official Government Service Workflows ---
        {
            "_id": "doc_id_address_alt",
            "name": "Aadhaar Card OR Voter ID Card OR Ration Card",
            "name_te": "ఆధార్ కార్డ్ / ఓటరు ఐడి / రేషన్ కార్డ్ (ఏదైనా ఒకటి)",
            "slug": "identity-address-alternative",
            "doc_type": "identity_address_alt",
            "icon": "🪪",
            "description": "Accepted identity/address proof: Upload any one of Aadhaar Card, Voter ID Card, or Ration Card.",
            "description_te": "గుర్తింపు / చిరునామా రుజువు: ఆధార్ కార్డ్, ఓటరు ఐడి లేదా రేషన్ కార్డులలో ఏదైనా ఒక పత్రం అప్‌లోడ్ చేయండి.",
            "expected_keywords": ["aadhaar", "voter id", "epic", "ration card", "uidai", "election commission", "civil supplies", "identity"]
        },
        {
            "_id": "doc_poi",
            "name": "Proof of Identity (POI)",
            "name_te": "గుర్తింపు రుజువు (POI)",
            "slug": "proof-of-identity",
            "doc_type": "proof_of_identity",
            "icon": "👤",
            "description": "One approved Proof of Identity document: Aadhaar Card, Voter ID, PAN Card, or Passport.",
            "description_te": "అధికారిక గుర్తింపు రుజువు పత్రం: ఆధార్, పాన్, ఓటరు ఐడి లేదా పాస్‌పోర్ట్.",
            "expected_keywords": ["proof of identity", "poi", "identity card", "pan", "voter id", "aadhaar", "passport", "name proof"]
        },
        {
            "_id": "doc_app_form",
            "name": "Application Form",
            "name_te": "దరఖాస్తు ఫారమ్",
            "slug": "application-form",
            "doc_type": "application_form",
            "icon": "📝",
            "description": "Duly signed official service application form prescribed by the respective government department.",
            "description_te": "సంబంధిత ప్రభుత్వ శాఖ నిర్దేశించిన సంతకం చేసిన అధికారిక దరఖాస్తు ఫారమ్.",
            "expected_keywords": ["application form", "applicant signature", "meeseva", "grama ward sachivalayam", "form", "declaration", "application"]
        },
        {
            "_id": "doc_medical_record",
            "name": "Doctor's Certificate / Medical Record",
            "name_te": "వైద్య ధృవీకరణ పత్రం / ఆసుపత్రి రికార్డు",
            "slug": "doctor-medical-certificate",
            "doc_type": "medical_record",
            "icon": "🏥",
            "description": "Doctor's certificate or institutional birth/medical discharge summary issued by a recognised medical authority.",
            "description_te": "గుర్తింపు పొందిన ఆసుపత్రి లేదా వైద్య అధికారి జారీ చేసిన జనన వైద్య ధృవీకరణ పత్రం.",
            "expected_keywords": ["doctor", "medical certificate", "hospital", "discharge summary", "delivery", "birth record", "medical officer", "dr"]
        },
        {
            "_id": "doc_non_avail_cert",
            "name": "Non-Availability Certificate",
            "name_te": "జనన వివరాలు లభ్యంకాని ధృవీకరణ పత్రం (NAC)",
            "slug": "non-availability-certificate",
            "doc_type": "non_avail_cert",
            "icon": "📑",
            "description": "Non-Availability Certificate (Form 10) issued by Gram Panchayat, Municipal Administration, or Registrar.",
            "description_te": "గ్రామ పంచాయతీ లేదా మున్సిపల్ కార్యాలయం జారీ చేసిన నాన్-అవైలబిలిటీ సర్టిఫికేట్ (NAC).",
            "expected_keywords": ["non-availability", "non availability", "form 10", "gram panchayat", "municipal", "registrar", "birth record not found"]
        },
        {
            "_id": "doc_self_affidavit",
            "name": "Self-Affidavit",
            "name_te": "స్వీయ ప్రమాణ పత్రం (అఫిడవిట్)",
            "slug": "self-affidavit",
            "doc_type": "self_affidavit",
            "icon": "⚖️",
            "description": "Notarized self-affidavit affirming date of birth, place of birth, or reason for delay on stamp paper.",
            "description_te": "నోటరీ ద్వారా ధృవీకరించబడిన స్టాంప్ పేపర్‌పై స్వీయ ప్రమాణ పత్రం (అఫిడవిట్).",
            "expected_keywords": ["affidavit", "self affidavit", "notary", "advocate", "sworn", "solemnly affirm", "stamp paper", "deponent"]
        },
        {
            "_id": "doc_death_cert",
            "name": "Death Certificate",
            "name_te": "మరణ ధృవీకరణ పత్రం",
            "slug": "death-certificate",
            "doc_type": "death_proof",
            "icon": "🕊️",
            "description": "Official Death Certificate issued by Municipal Corporation, Gram Panchayat, or Registrar of Deaths.",
            "description_te": "మున్సిపల్ కార్పొరేషన్ లేదా పంచాయతీ జారీ చేసిన అధికారిక మరణ ధృవీకరణ పత్రం.",
            "expected_keywords": ["death certificate", "registrar of births and deaths", "date of death", "place of death", "deceased"]
        },
        {
            "_id": "doc_marriage_cert",
            "name": "Marriage Certificate",
            "name_te": "వివాహ ధృవీకరణ పత్రం",
            "slug": "marriage-certificate",
            "doc_type": "marriage_proof",
            "icon": "💍",
            "description": "Official Marriage Certificate issued by Sub-Registrar / Municipal Registrar, or Wedding Invitation Card.",
            "description_te": "సబ్-రిజిస్ట్రార్ కార్యాలయం జారీ చేసిన వివాహ రిజిస్ట్రేషన్ పత్రం.",
            "expected_keywords": ["marriage certificate", "marriage registration", "sub registrar", "bride", "bridegroom", "wedding", "husband", "wife"]
        },
        {
            "_id": "doc_schedule_docs",
            "name": "Schedule I to IV Documents / Revenue Records",
            "name_te": "షెడ్యూల్ I నుండి IV పత్రాలు / రెవెన్యూ రికార్డులు",
            "slug": "schedule-documents",
            "doc_type": "schedule_docs",
            "icon": "📁",
            "description": "Statutory Schedule I to IV inquiry reports, family tree verification, or Revenue Tahsildar records.",
            "description_te": "చట్టబద్ధమైన షెడ్యూల్ I నుండి IV విచారణ నివేదికలు మరియు రెవెన్యూ రికార్డులు.",
            "expected_keywords": ["schedule i", "schedule ii", "schedule iii", "schedule iv", "revenue records", "inquiry report", "genealogy", "family tree"]
        },
        {
            "_id": "doc_fir_report",
            "name": "Old/Mutilated Voter ID OR FIR/Police Report",
            "name_te": "పాత/పాడైన ఓటరు ఐడి లేదా FIR/పోలీస్ నివేదిక",
            "slug": "fir-police-report",
            "doc_type": "fir_police_report",
            "icon": "🚓",
            "description": "Original mutilated voter card or Police FIR / Lost Document Certificate for replacement of lost/damaged EPIC.",
            "description_te": "ఓటరు ఐడి కార్డు రీప్లేస్‌మెంట్ కోసం పాడైన కార్డు లేదా పోలీస్ FIR / నష్టపోయిన పత్ర ధృవీకరణ.",
            "expected_keywords": ["fir", "first information report", "police", "lost certificate", "mutilated", "damaged voter id", "police station"]
        },
        {
            "_id": "doc_nativity_cert",
            "name": "Nativity / Residence Certificate",
            "name_te": "నివాస / స్థానికత ధృవీకరణ పత్రం",
            "slug": "nativity-certificate",
            "doc_type": "nativity_cert",
            "icon": "🏡",
            "description": "Official Nativity / Residence / Domicile Certificate issued by Tahsildar for scholarships and admissions.",
            "description_te": "స్కాలర్‌షిప్‌లు మరియు అడ్మిషన్ల కోసం తహశీల్దార్ జారీ చేసిన స్థానికత / నివాస ధృవీకరణ పత్రం.",
            "expected_keywords": ["nativity certificate", "residence certificate", "domicile", "native of", "tahsildar", "mandal"]
        },
        {
            "_id": "doc_correction_proof",
            "name": "Supporting Document for Correction",
            "name_te": "సవరణకు ఆధారమైన పత్రం",
            "slug": "correction-proof",
            "doc_type": "correction_proof",
            "icon": "🔍",
            "description": "Documentary proof verifying the specific detail requested for correction or update.",
            "description_te": "దరఖాస్తులో సవరించదలిచిన వివరాలకు సంబంధించిన అధికారిక ఆధార పత్రం.",
            "expected_keywords": ["proof", "correction", "evidence", "supporting document", "gazette", "certificate", "name change", "dob proof"]
        }
    ]
    documents_col.insert_many(documents)

    print("Seeding 8 Official Government Services + Unified Service...")
    services = [
        {
            "_id": "srv_income_cert",
            "name": "Income Certificate",
            "name_te": "ఆదాయ ధృవీకరణ పత్రం",
            "slug": "income-certificate",
            "description": "Official government certificate verifying family annual income for welfare schemes, fee reimbursement, and quota applications.",
            "description_te": "సంక్షేమ పథకాలు మరియు ఫీజు రీయింబర్స్‌మెంట్ కోసం కుటుంబ వార్షిక ఆదాయాన్ని ధృవీకరించే అధికారిక పత్రం.",
            "department": "Revenue & Land Records Department",
            "department_te": "రెవెన్యూ మరియు భూ రికార్డుల శాఖ",
            "icon": "📄",
            "has_update": True,
            "official_portal_url": "https://services.india.gov.in/",
            "is_active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        },
        {
            "_id": "srv_caste_cert",
            "name": "Caste Certificate",
            "name_te": "కుల ధృవీకరణ పత్రం",
            "slug": "caste-certificate",
            "description": "Official Integrated Caste-Nativity-DOB Certificate issued by Revenue Tahsildar for reservations and welfare programs.",
            "description_te": "రిజర్వేషన్లు మరియు సంక్షేమ పథకాల కోసం తహశీల్దార్ జారీ చేసే సమగ్ర కుల-స్థానికత-జనన ధృవీకరణ పత్రం.",
            "department": "Department of Backward Classes & Tribal Welfare",
            "department_te": "వెనుకబడిన తరగతులు మరియు గిరిజన సంక్షేమ శాఖ",
            "icon": "📜",
            "has_update": True,
            "official_portal_url": "https://services.india.gov.in/",
            "is_active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        },
        {
            "_id": "srv_birth_cert",
            "name": "Birth Certificate",
            "name_te": "జనన ధృవీకరణ పత్రం",
            "slug": "birth-certificate",
            "description": "Official birth certificate issued by Municipal Administration, Gram Panchayat, or Registrar of Births and Deaths.",
            "description_te": "పురపాలక శాఖ లేదా గ్రామ పంచాయతీ జారీ చేసే అధికారిక జనన ధృవీకరణ పత్రం.",
            "department": "Municipal Administration & Urban Development",
            "department_te": "పురపాలక పరిపాలన మరియు పట్టణాభివృద్ధి శాఖ",
            "icon": "👶",
            "has_update": False,
            "official_portal_url": "https://services.india.gov.in/",
            "is_active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        },
        {
            "_id": "srv_aadhaar_card",
            "name": "Aadhaar Card",
            "name_te": "ఆధార్ కార్డ్",
            "slug": "aadhaar-card",
            "description": "12-digit Unique Identification Number issued by UIDAI for resident identity verification.",
            "description_te": "భారత విశిష్ట గుర్తింపు ప్రాధికార సంస్థ (UIDAI) జారీ చేసే 12 అంకెల విశిష్ట గుర్తింపు కార్డు.",
            "department": "Unique Identification Authority of India (UIDAI)",
            "department_te": "భారత విశిష్ట గుర్తింపు ప్రాధికార సంస్థ (UIDAI)",
            "icon": "🆔",
            "has_update": True,
            "official_portal_url": "https://myaadhaar.uidai.gov.in/",
            "is_active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        },
        {
            "_id": "srv_pan_card",
            "name": "PAN Card",
            "name_te": "పాన్ కార్డ్",
            "slug": "pan-card",
            "description": "Permanent Account Number issued by Income Tax Department & Protean / NSDL for financial operations.",
            "description_te": "ఆదాయ పన్ను శాఖ మరియు ప్రొటీన్ జారీ చేసే శాశ్వత ఖాతా సంఖ్య (PAN).",
            "department": "Income Tax Department & NSDL / Protean",
            "department_te": "ఆదాయ పన్ను శాఖ & ప్రొటీన్",
            "icon": "💳",
            "has_update": True,
            "official_portal_url": "https://www.onlineservices.nsdl.com/",
            "is_active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        },
        {
            "_id": "srv_voter_id",
            "name": "Voter ID Card",
            "name_te": "ఓటరు గుర్తింపు కార్డ్",
            "slug": "voter-id-card",
            "description": "Electoral Photo Identity Card (EPIC) issued by Election Commission of India for franchise rights.",
            "description_te": "భారత ఎన్నికల సంఘం జారీ చేసే ఓటరు ఫోటో గుర్తింపు కార్డు (EPIC).",
            "department": "Election Commission of India (ECI)",
            "department_te": "భారత ఎన్నికల సంఘం",
            "icon": "🗳️",
            "has_update": True,
            "official_portal_url": "https://voters.eci.gov.in/",
            "is_active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        },
        {
            "_id": "srv_scholarship",
            "name": "Scholarship Application",
            "name_te": "స్కాలర్‌షిప్ దరఖాస్తు",
            "slug": "scholarship-application",
            "description": "State & National portal verification for post-matric fee reimbursement and educational scholarships (Jagananna Vidya Deevena).",
            "description_te": "విద్యార్థుల పోస్ట్-మెట్రిక్ ఫీజు రీయింబర్స్‌మెంట్ మరియు విద్యా స్కాలర్‌షిప్‌ల కోసం ధృవీకరణ.",
            "department": "Ministry of Social Justice & State Social Welfare",
            "department_te": "సాంఘిక సంక్షేమ శాఖ",
            "icon": "🎓",
            "has_update": False,
            "official_portal_url": "https://services.india.gov.in/",
            "is_active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        },
        {
            "_id": "srv_ration_card",
            "name": "Ration Card",
            "name_te": "రేషన్ కార్డ్",
            "slug": "ration-card",
            "description": "Food Security Rice Card issued by Civil Supplies Department for subsidized food grains and welfare identification.",
            "description_te": "పౌర సరఫరాల శాఖ జారీ చేసే బియ్యం కార్డు / ఆహార భద్రతా రేషన్ కార్డు.",
            "department": "Department of Food & Civil Supplies",
            "department_te": "పౌర సరఫరాలు మరియు వినియోగదారుల వ్యవహారాల శాఖ",
            "icon": "🍚",
            "has_update": True,
            "official_portal_url": "https://services.india.gov.in/",
            "is_active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        },
        {
            "_id": "srv_gov_doc_verify",
            "name": "Government Document Verification",
            "name_te": "ప్రభుత్వ పత్రాల పరిశీలన",
            "slug": "government-document-verification",
            "description": "Upload and verify various government-related documents through a single AI-powered document verification system.",
            "description_te": "ఏకీకృత AI ఆధారిత పత్రాల పరిశీలన వ్యవస్థ ద్వారా వివిధ ప్రభుత్వ సంబంధిత పత్రాలను అప్‌లోడ్ చేసి పరిశీలించండి.",
            "department": "Public Document Verification Authority",
            "department_te": "ప్రభుత్వ పత్రాల పరిశీలన సంస్థ",
            "icon": "🏛️",
            "has_update": True,
            "official_portal_url": "https://services.india.gov.in/",
            "is_active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
    ]
    services_col.insert_many(services)

    print("Mapping Exact Service-Wise Document Checklists...")
    service_documents = [
        # =========================================================================
        # 1. INCOME CERTIFICATE
        # =========================================================================
        # New Application:
        # 1. Aadhaar Card OR Voter ID Card OR Ration Card (Upload any one)
        # 2. Income Proof - Salary Slips OR IT Returns OR other accepted income proof
        # 3. Application Form
        {"service_id": "srv_income_cert", "document_id": "doc_id_address_alt", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "alt", "display_order": 1},
        {"service_id": "srv_income_cert", "document_id": "doc_salary_slip", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_income_cert", "document_id": "doc_app_form", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},

        # Update:
        # 1. Existing Income Certificate
        # 2. Aadhaar Card
        # 3. Supporting document for the particular correction
        {"service_id": "srv_income_cert", "document_id": "doc_income_cert", "application_type": "update", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_income_cert", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_income_cert", "document_id": "doc_correction_proof", "application_type": "update", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},

        # =========================================================================
        # 2. CASTE CERTIFICATE (Integrated Caste-Nativity-DOB Certificate)
        # =========================================================================
        # New Application:
        # 1. Family Member's Previously Issued Caste Certificate (if available/applicable)
        # 2. SSC Marks Memo OR DOB Extract OR Transfer Certificate (Upload Any One)
        # 3. 1st to 10th Study and Conduct Certificates OR applicable DOB Certificate (Upload Any One)
        # 4. Aadhaar Card OR Voter ID Card OR Ration Card (Upload Any One)
        # 5. Schedule I to IV Documents (Required only if applicable)
        # 6. Application Form
        {"service_id": "srv_caste_cert", "document_id": "doc_family_caste_cert", "application_type": "new", "sub_operation": "", "is_mandatory": False, "badge_type": "conditional", "display_order": 1},
        {"service_id": "srv_caste_cert", "document_id": "doc_tenth_memo", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "alt", "display_order": 2},
        {"service_id": "srv_caste_cert", "document_id": "doc_study_cert", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "alt", "display_order": 3},
        {"service_id": "srv_caste_cert", "document_id": "doc_id_address_alt", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "alt", "display_order": 4},
        {"service_id": "srv_caste_cert", "document_id": "doc_schedule_docs", "application_type": "new", "sub_operation": "", "is_mandatory": False, "badge_type": "conditional", "display_order": 5},
        {"service_id": "srv_caste_cert", "document_id": "doc_app_form", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 6},

        # Update:
        # 1. Existing Caste/Integrated Certificate
        # 2. Aadhaar Card
        # 3. Supporting document related to the specific correction requested
        # 4. Family Member's Previously Issued Caste Certificate (only if relevant to the correction)
        {"service_id": "srv_caste_cert", "document_id": "doc_caste_cert", "application_type": "update", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_caste_cert", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_caste_cert", "document_id": "doc_correction_proof", "application_type": "update", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},
        {"service_id": "srv_caste_cert", "document_id": "doc_family_caste_cert", "application_type": "update", "sub_operation": "", "is_mandatory": False, "badge_type": "conditional", "display_order": 4},

        # =========================================================================
        # 3. BIRTH CERTIFICATE
        # =========================================================================
        # New Application - Normal (within 1 year):
        # 1. Doctor's Certificate / Medical Record
        # 2. Application Form
        {"service_id": "srv_birth_cert", "document_id": "doc_medical_record", "application_type": "new", "sub_operation": "normal", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_birth_cert", "document_id": "doc_app_form", "application_type": "new", "sub_operation": "normal", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # New Application - Late (after 1 year):
        # 1. Non-Availability Certificate from Gram Panchayat / Municipal Administration
        # 2. Ration Card
        # 3. SSC Marks Memo, where applicable
        # 4. Self-Affidavit
        # 5. Relevant physical supporting document
        {"service_id": "srv_birth_cert", "document_id": "doc_non_avail_cert", "application_type": "new", "sub_operation": "late", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_birth_cert", "document_id": "doc_ration_card", "application_type": "new", "sub_operation": "late", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_birth_cert", "document_id": "doc_tenth_memo", "application_type": "new", "sub_operation": "late", "is_mandatory": False, "badge_type": "conditional", "display_order": 3},
        {"service_id": "srv_birth_cert", "document_id": "doc_self_affidavit", "application_type": "new", "sub_operation": "late", "is_mandatory": True, "badge_type": "mandatory", "display_order": 4},
        {"service_id": "srv_birth_cert", "document_id": "doc_correction_proof", "application_type": "new", "sub_operation": "late", "is_mandatory": True, "badge_type": "mandatory", "display_order": 5},

        # =========================================================================
        # 4. AADHAAR CARD
        # =========================================================================
        # New Application:
        # 1. Proof of Identity (POI)
        # 2. Proof of Address (POA)
        # 3. Proof of Date of Birth (PDB) - if DOB needs to be recorded as verified
        {"service_id": "srv_aadhaar_card", "document_id": "doc_poi", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_aadhaar_card", "document_id": "doc_address_proof", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_aadhaar_card", "document_id": "doc_birth_cert", "application_type": "new", "sub_operation": "", "is_mandatory": False, "badge_type": "conditional", "display_order": 3},

        # Update Sub-operations:
        # Name Update: Existing Aadhaar + POI
        {"service_id": "srv_aadhaar_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "name", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_aadhaar_card", "document_id": "doc_poi", "application_type": "update", "sub_operation": "name", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # Address Update: Existing Aadhaar + Address Proof (POA)
        {"service_id": "srv_aadhaar_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "address", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_aadhaar_card", "document_id": "doc_address_proof", "application_type": "update", "sub_operation": "address", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # DOB Update: Existing Aadhaar + DOB Proof
        {"service_id": "srv_aadhaar_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "dob", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_aadhaar_card", "document_id": "doc_birth_cert", "application_type": "update", "sub_operation": "dob", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # Gender Update: Existing Aadhaar + Evidence/Medical Proof
        {"service_id": "srv_aadhaar_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "gender", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_aadhaar_card", "document_id": "doc_correction_proof", "application_type": "update", "sub_operation": "gender", "is_mandatory": False, "badge_type": "conditional", "display_order": 2},

        # Mobile/Email Update: Existing Aadhaar details (centre biometric update, no extra document)
        {"service_id": "srv_aadhaar_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "mobile_email", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},

        # Photo/Biometrics Update: Existing Aadhaar (enrolment centre update)
        {"service_id": "srv_aadhaar_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "biometrics", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},

        # POI/POA Document Update: Existing Aadhaar + POI + POA
        {"service_id": "srv_aadhaar_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "document_update", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_aadhaar_card", "document_id": "doc_poi", "application_type": "update", "sub_operation": "document_update", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_aadhaar_card", "document_id": "doc_address_proof", "application_type": "update", "sub_operation": "document_update", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},

        # =========================================================================
        # 5. PAN CARD
        # =========================================================================
        # New Application:
        # 1. Proof of Identity
        # 2. Proof of Address
        # 3. Proof of Date of Birth
        # 4. Photograph and Signature
        {"service_id": "srv_pan_card", "document_id": "doc_poi", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_pan_card", "document_id": "doc_address_proof", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_pan_card", "document_id": "doc_birth_cert", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},
        {"service_id": "srv_pan_card", "document_id": "doc_passport_photo", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 4},

        # Update Sub-operations:
        # Name correction: Existing PAN + Name proof (POI)
        {"service_id": "srv_pan_card", "document_id": "doc_pan", "application_type": "update", "sub_operation": "name", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_pan_card", "document_id": "doc_poi", "application_type": "update", "sub_operation": "name", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # DOB correction: Existing PAN + DOB proof
        {"service_id": "srv_pan_card", "document_id": "doc_pan", "application_type": "update", "sub_operation": "dob", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_pan_card", "document_id": "doc_birth_cert", "application_type": "update", "sub_operation": "dob", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # Other personal detail correction: Existing PAN + proof relevant to that field
        {"service_id": "srv_pan_card", "document_id": "doc_pan", "application_type": "update", "sub_operation": "personal", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_pan_card", "document_id": "doc_correction_proof", "application_type": "update", "sub_operation": "personal", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # Address/contact update: Existing PAN + address proof
        {"service_id": "srv_pan_card", "document_id": "doc_pan", "application_type": "update", "sub_operation": "address", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_pan_card", "document_id": "doc_address_proof", "application_type": "update", "sub_operation": "address", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # PAN Reprint: Existing PAN details only
        {"service_id": "srv_pan_card", "document_id": "doc_pan", "application_type": "update", "sub_operation": "reprint", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},

        # =========================================================================
        # 6. VOTER ID CARD
        # =========================================================================
        # New Application:
        # 1. Recent Passport Size Photograph
        # 2. Age Proof (Form 6)
        # 3. Address Proof
        {"service_id": "srv_voter_id", "document_id": "doc_passport_photo", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_voter_id", "document_id": "doc_birth_cert", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_voter_id", "document_id": "doc_address_proof", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},

        # Update (Form 8 sub-operations):
        # Shifting of Residence: Existing Voter ID + New Address Proof
        {"service_id": "srv_voter_id", "document_id": "doc_voter_id", "application_type": "update", "sub_operation": "shifting", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_voter_id", "document_id": "doc_address_proof", "application_type": "update", "sub_operation": "shifting", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # Correction of Entries: Existing Voter ID + Supporting proof for selected correction
        {"service_id": "srv_voter_id", "document_id": "doc_voter_id", "application_type": "update", "sub_operation": "correction", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_voter_id", "document_id": "doc_correction_proof", "application_type": "update", "sub_operation": "correction", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # Photograph Change: Existing Voter ID + Recent Passport Photo
        {"service_id": "srv_voter_id", "document_id": "doc_voter_id", "application_type": "update", "sub_operation": "photo", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_voter_id", "document_id": "doc_passport_photo", "application_type": "update", "sub_operation": "photo", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # Replacement of Lost/Damaged EPIC: Existing Voter ID + Old/Mutilated Voter ID OR FIR/Police Report
        {"service_id": "srv_voter_id", "document_id": "doc_voter_id", "application_type": "update", "sub_operation": "replacement", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_voter_id", "document_id": "doc_fir_report", "application_type": "update", "sub_operation": "replacement", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # =========================================================================
        # 7. SCHOLARSHIP APPLICATION (NEW ONLY)
        # =========================================================================
        # 1. Caste Certificate
        # 2. Income Certificate
        # 3. Aadhaar Card
        # 4. Ration Card - if available/required
        # 5. SSC Marks Memo / DOB Proof
        # 6. Qualifying Educational Marks Memo
        # 7. College Admission / Allotment Order
        # 8. Father's Aadhaar Card
        # 9. Mother's Aadhaar Card
        # 10. Bank Passbook - only where required
        # 11. Passport Size Photo - if required
        {"service_id": "srv_scholarship", "document_id": "doc_caste_cert", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_scholarship", "document_id": "doc_income_cert", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_scholarship", "document_id": "doc_aadhaar", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},
        {"service_id": "srv_scholarship", "document_id": "doc_ration_card", "application_type": "new", "sub_operation": "", "is_mandatory": False, "badge_type": "conditional", "display_order": 4},
        {"service_id": "srv_scholarship", "document_id": "doc_tenth_memo", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 5},
        {"service_id": "srv_scholarship", "document_id": "doc_inter_memo", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 6},
        {"service_id": "srv_scholarship", "document_id": "doc_college_allotment", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 7},
        {"service_id": "srv_scholarship", "document_id": "doc_father_aadhaar", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 8},
        {"service_id": "srv_scholarship", "document_id": "doc_mother_aadhaar", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 9},
        {"service_id": "srv_scholarship", "document_id": "doc_bank_passbook", "application_type": "new", "sub_operation": "", "is_mandatory": False, "badge_type": "conditional", "display_order": 10},
        {"service_id": "srv_scholarship", "document_id": "doc_passport_photo", "application_type": "new", "sub_operation": "", "is_mandatory": False, "badge_type": "conditional", "display_order": 11},

        # =========================================================================
        # 8. RATION CARD
        # =========================================================================
        # New Application:
        # 1. Aadhaar Card details of all family members
        # 2. Address Proof
        # 3. Income Certificate
        {"service_id": "srv_ration_card", "document_id": "doc_aadhaar", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_ration_card", "document_id": "doc_address_proof", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_ration_card", "document_id": "doc_income_cert", "application_type": "new", "sub_operation": "", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},

        # Update Sub-operations:
        # Member Addition: Existing Ration Card + Aadhaar of new member
        {"service_id": "srv_ration_card", "document_id": "doc_ration_card", "application_type": "update", "sub_operation": "member_addition", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_ration_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "member_addition", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},

        # Member Deletion: Existing Ration Card + Aadhaar of member to be deleted + Relevant supporting proof
        {"service_id": "srv_ration_card", "document_id": "doc_ration_card", "application_type": "update", "sub_operation": "member_deletion", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_ration_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "member_deletion", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_ration_card", "document_id": "doc_correction_proof", "application_type": "update", "sub_operation": "member_deletion", "is_mandatory": False, "badge_type": "conditional", "display_order": 3},

        # Address Change: Existing Ration Card + Aadhaar Card + New Address Proof
        {"service_id": "srv_ration_card", "document_id": "doc_ration_card", "application_type": "update", "sub_operation": "address_change", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_ration_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "address_change", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_ration_card", "document_id": "doc_address_proof", "application_type": "update", "sub_operation": "address_change", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},

        # Member/Family Details Correction: Existing Ration Card + Aadhaar Card + Supporting document
        {"service_id": "srv_ration_card", "document_id": "doc_ration_card", "application_type": "update", "sub_operation": "correction", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_ration_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "correction", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_ration_card", "document_id": "doc_correction_proof", "application_type": "update", "sub_operation": "correction", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},

        # Ration Card Splitting: Existing Ration Card + Aadhaar of family members + Address Proof
        {"service_id": "srv_ration_card", "document_id": "doc_ration_card", "application_type": "update", "sub_operation": "splitting", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_ration_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "splitting", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_ration_card", "document_id": "doc_address_proof", "application_type": "update", "sub_operation": "splitting", "is_mandatory": False, "badge_type": "conditional", "display_order": 3},

        # Ration Card Surrender: Existing Ration Card + Aadhaar + Surrender supporting document
        {"service_id": "srv_ration_card", "document_id": "doc_ration_card", "application_type": "update", "sub_operation": "surrender", "is_mandatory": True, "badge_type": "mandatory", "display_order": 1},
        {"service_id": "srv_ration_card", "document_id": "doc_aadhaar", "application_type": "update", "sub_operation": "surrender", "is_mandatory": True, "badge_type": "mandatory", "display_order": 2},
        {"service_id": "srv_ration_card", "document_id": "doc_correction_proof", "application_type": "update", "sub_operation": "surrender", "is_mandatory": True, "badge_type": "mandatory", "display_order": 3},

        # =========================================================================
        # 9. UNIFIED COMMON SERVICE (Restored on "Clear Selection" / Overview)
        # =========================================================================
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_aadhaar", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 1},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_pan", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 2},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_voter_id", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 3},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_caste_cert", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 4},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_income_cert", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 5},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_bank_passbook", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 6},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_passport_photo", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 7},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_ration_card", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 8},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_study_cert", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 9},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_tenth_memo", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 10},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_inter_memo", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 11},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_father_aadhaar", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 12},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_mother_aadhaar", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 13},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_birth_cert", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 14},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_college_allotment", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 15},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_salary_slip", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 16},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_family_caste_cert", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 17},
        {"service_id": "srv_gov_doc_verify", "document_id": "doc_address_proof", "application_type": "all", "sub_operation": "", "is_mandatory": False, "badge_type": "optional", "display_order": 18}
    ]
    service_docs_col.insert_many(service_documents)

    # Seed User Accounts
    users_col = get_users_collection()
    from services.auth_service import AuthService
    default_password_hash = AuthService.hash_password("SecretPassword123!")

    initial_users = [
        "varshinipriyaarepalli12@gmail.com",
        "varshinipriyaarepalli@gmail.com",
        "varshinipriyaarepalli17@gmail.com",
        "nirishapriyaarepalli16@gmail.com",
        "srivallich861@gmail.com"
    ]

    for email in initial_users:
        if not users_col.find_one({"email": email}):
            users_col.insert_one({
                "_id": f"usr_{email.split('@')[0]}",
                "name": email.split("@")[0].replace(".", " ").title(),
                "email": email,
                "password_hash": default_password_hash,
                "created_at": datetime.datetime.now(datetime.timezone.utc)
            })

    print(f"Database successfully seeded with {len(services)} services, {len(documents)} document definitions, and {len(service_documents)} service document mappings.")

if __name__ == "__main__":
    seed_database()
