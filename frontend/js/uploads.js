// State Management for Dynamic Government Services & Application Types (New vs Update)
let currentService = null;
let currentServiceSlug = "income-certificate";
let currentApplicationType = "new"; // "new" | "update" | "all"
let currentSubOperation = ""; // e.g. "normal" | "late" | "name" | "address" etc.
let requiredDocuments = [];
let uploadedFilesMap = {}; // document_id -> upload object
let activeSessionId = null;

// Official 8 Government Services with Bilingual Metadata
const OFFICIAL_SERVICES = [
  {
    slug: "income-certificate",
    id: "srv_income_cert",
    name: "Income Certificate",
    name_te: "ఆదాయ ధృవీకరణ పత్రం",
    department: "Revenue & Land Records",
    department_te: "రెవెన్యూ శాఖ",
    icon: "📄",
    has_update: true
  },
  {
    slug: "caste-certificate",
    id: "srv_caste_cert",
    name: "Caste Certificate",
    name_te: "కుల ధృవీకరణ పత్రం",
    department: "Backward Classes & Tribal Welfare",
    department_te: "వెనుకబడిన తరగతులు & గిరిజన సంక్షేమ శాఖ",
    icon: "📜",
    has_update: true
  },
  {
    slug: "birth-certificate",
    id: "srv_birth_cert",
    name: "Birth Certificate",
    name_te: "జనన ధృవీకరణ పత్రం",
    department: "Municipal Administration",
    department_te: "పురపాలక పరిపాలన శాఖ",
    icon: "👶",
    has_update: false
  },
  {
    slug: "aadhaar-card",
    id: "srv_aadhaar_card",
    name: "Aadhaar Card",
    name_te: "ఆధార్ కార్డ్",
    department: "UIDAI",
    department_te: "భారత విశిష్ట గుర్తింపు ప్రాధికార సంస్థ",
    icon: "🆔",
    has_update: true
  },
  {
    slug: "pan-card",
    id: "srv_pan_card",
    name: "PAN Card",
    name_te: "పాన్ కార్డ్",
    department: "Income Tax Department & Protean",
    department_te: "ఆదాయ పన్ను శాఖ",
    icon: "💳",
    has_update: true
  },
  {
    slug: "voter-id-card",
    id: "srv_voter_id",
    name: "Voter ID Card",
    name_te: "ఓటరు గుర్తింపు కార్డ్",
    department: "Election Commission of India",
    department_te: "భారత ఎన్నికల సంఘం",
    icon: "🗳️",
    has_update: true
  },
  {
    slug: "scholarship-application",
    id: "srv_scholarship",
    name: "Scholarship Application",
    name_te: "స్కాలర్‌షిప్ దరఖాస్తు",
    department: "Social Welfare Department",
    department_te: "సాంఘిక సంక్షేమ శాఖ",
    icon: "🎓",
    has_update: false // Scholarship only provides New Application
  },
  {
    slug: "ration-card",
    id: "srv_ration_card",
    name: "Ration Card",
    name_te: "రేషన్ కార్డ్",
    department: "Food & Civil Supplies",
    department_te: "పౌర సరఫరాల శాఖ",
    icon: "🍚",
    has_update: true
  }
];

// Document Metadata Catalog for 30 Approved Document Types
const DOCUMENT_DEFINITIONS = {
  "doc_aadhaar": {
    name: "Aadhaar Card",
    name_te: "ఆధార్ కార్డ్",
    icon: "🆔",
    description: "Government of India Unique Identification Card containing 12-digit Aadhaar number issued by UIDAI.",
    description_te: "UIDAI జారీ చేసిన 12 అంకెల ఆధార్ సంఖ్య కలిగిన భారత ప్రభుత్వ విశిష్ట గుర్తింపు కార్డు."
  },
  "doc_pan": {
    name: "PAN Card",
    name_te: "పాన్ కార్డ్",
    icon: "💳",
    description: "Permanent Account Number Card issued by Income Tax Department, Government of India.",
    description_te: "భారత ప్రభుత్వ ఆదాయ పన్ను శాఖ జారీ చేసిన శాశ్వత ఖాతా సంఖ్య (PAN) కార్డు."
  },
  "doc_voter_id": {
    name: "Voter ID Card",
    name_te: "ఓటరు గుర్తింపు కార్డ్",
    icon: "🗳️",
    description: "Electoral Photo Identity Card (EPIC) issued by Election Commission of India.",
    description_te: "భారత ఎన్నికల సంఘం జారీ చేసిన ఓటరు ఫోటో గుర్తింపు కార్డు (EPIC)."
  },
  "doc_caste_cert": {
    name: "Caste Certificate",
    name_te: "కుల ధృవీకరణ పత్రం",
    icon: "📜",
    description: "Official Community / Caste / Integrated Certificate issued by Revenue Tahsildar.",
    description_te: "రెవెన్యూ తహశీల్దార్ జారీ చేసిన అధికారిక కుల ధృవీకరణ పత్రం."
  },
  "doc_income_cert": {
    name: "Income Certificate",
    name_te: "ఆదాయ ధృవీకరణ పత్రం",
    icon: "📄",
    description: "Official Income Certificate issued by Revenue Tahsildar.",
    description_te: "రెవెన్యూ శాఖ తహశీల్దార్ జారీ చేసిన అధికారిక ఆదాయ ధృవీకరణ పత్రం."
  },
  "doc_bank_passbook": {
    name: "Bank Passbook",
    name_te: "బ్యాంక్ పాస్‌బుక్",
    icon: "🏦",
    description: "First page of Bank Passbook showing Account Number, Account Holder Name, IFSC code, and Branch stamp.",
    description_te: "ఖాతా సంఖ్య మరియు IFSC కోడ్ కలిగిన బ్యాంక్ పాస్‌బుక్ మొదటి పేజీ."
  },
  "doc_passport_photo": {
    name: "Passport Size Photo",
    name_te: "పాస్‌పోర్ట్ సైజ్ ఫోటో",
    icon: "📷",
    description: "Recent color front-facing passport size portrait photograph of applicant.",
    description_te: "దరఖాస్తుదారుడి ఇటీవలి పాస్‌పోర్ట్ సైజ్ ఫోటోగ్రాఫ్."
  },
  "doc_ration_card": {
    name: "Ration Card",
    name_te: "రేషన్ కార్డ్",
    icon: "🍚",
    description: "Department of Food & Civil Supplies Ration Card or Rice Card.",
    description_te: "పౌర సరఫరాల శాఖ రేషన్ కార్డు లేదా రైస్ కార్డు."
  },
  "doc_study_cert": {
    name: "Study and Conduct Certificate",
    name_te: "స్టడీ మరియు కాండక్ట్ సర్టిఫికేట్",
    icon: "🎓",
    description: "1st to 10th Study and Conduct Certificate, Bonafide Certificate, or School/College Conduct Certificate.",
    description_te: "గుర్తింపు పొందిన విద్యాసంస్థ జారీ చేసిన స్టడీ మరియు కాండక్ట్ సర్టిఫికేట్ లేదా బోనాఫైడ్ సర్టిఫికేట్."
  },
  "doc_tenth_memo": {
    name: "SSC Marks Memo",
    name_te: "10వ తరగతి మార్కుల మెమో (SSC)",
    icon: "📋",
    description: "SSC Marks Memo OR DOB Extract OR Transfer Certificate.",
    description_te: "సెకండరీ స్కూల్ సర్టిఫికేట్ (SSC) / 10వ తరగతి మార్కుల మెమో లేదా బదిలీ పత్రం (TC)."
  },
  "doc_inter_memo": {
    name: "Qualifying Educational Marks Memo",
    name_te: "ఇంటర్మీడియట్ / అర్హత విద్యా మార్కుల మెమో",
    icon: "📊",
    description: "Board of Intermediate Education / Higher Secondary (10+2) Qualifying Marks Memorandum.",
    description_te: "ఇంటర్మీడియట్ (+2) లేదా అర్హత పరీక్ష అధికారిక మార్కుల మెమో."
  },
  "doc_father_aadhaar": {
    name: "Father's Aadhaar Card",
    name_te: "తండ్రి ఆధార్ కార్డ్",
    icon: "👨",
    description: "Unique Identification (Aadhaar) Card of Father issued by UIDAI.",
    description_te: "తండ్రి యొక్క భారత ప్రభుత్వ ఆధార్ కార్డు."
  },
  "doc_mother_aadhaar": {
    name: "Mother's Aadhaar Card",
    name_te: "తల్లి ఆధార్ కార్డ్",
    icon: "👩",
    description: "Unique Identification (Aadhaar) Card of Mother issued by UIDAI.",
    description_te: "తల్లి యొక్క భారత ప్రభుత్వ ఆధార్ కార్డు."
  },
  "doc_birth_cert": {
    name: "Birth Certificate / Age Proof",
    name_te: "జనన ధృవీకరణ పత్రం / వయస్సు రుజువు",
    icon: "👶",
    description: "Official Birth Certificate issued by Municipal Corporation, Registrar, or Hospital / Age Proof.",
    description_te: "మున్సిపల్ కార్పొరేషన్ లేదా జనన రిజిస్ట్రార్ జారీ చేసిన జనన ధృవీకరణ పత్రం."
  },
  "doc_college_allotment": {
    name: "College Admission / Allotment Order",
    name_te: "కళాశాల ప్రవేశం / అలాట్‌మెంట్ ఆర్డర్",
    icon: "🏛️",
    description: "Official College Seat Allotment Order, Admission Letter, or Joining Report issued by Convener / University.",
    description_te: "కన్వీనర్ లేదా విశ్వవిద్యాలయం జారీ చేసిన అధికారిక కళాశాల సీటు అలాట్‌మెంట్ ఆర్డర్ లేదా అడ్మిషన్ లెటర్."
  },
  "doc_salary_slip": {
    name: "Income Proof – Salary Slips / IT Returns",
    name_te: "ఆదాయ రుజువు (జీతపు స్లిప్పులు / IT రిటర్న్స్)",
    icon: "💵",
    description: "Income Proof – Salary Slips OR IT Returns OR other accepted income proof.",
    description_te: "ఉద్యోగి నెలవారీ వేతనం లేదా ఆదాయాన్ని చూపే శాలరీ స్లిప్ / IT రిటర్న్స్."
  },
  "doc_family_caste_cert": {
    name: "Family Member's Previously Issued Caste Certificate",
    name_te: "కుటుంబ సభ్యుల మునుపటి కుల ధృవీకరణ పత్రం",
    icon: "📜",
    description: "Previously issued Government Caste / Community Certificate of Father, Mother, Brother, or Sister.",
    description_te: "తండ్రి, తల్లి, సోదరుడు లేదా సోదరి పేరుతో రెవెన్యూ అధికారి జారీ చేసిన మునుపటి కుల ధృవీకరణ పత్రం."
  },
  "doc_address_proof": {
    name: "Address Proof",
    name_te: "చిరునామా రుజువు",
    icon: "🏠",
    description: "Valid address proof: Ration Card / Voter ID / Aadhaar Card / House Tax Receipt / Telephone Bill / Electricity Bill.",
    description_te: "చెల్లుబాటు అయ్యే చిరునామా రుజువు: రేషన్ కార్డ్ / ఓటరు ఐడి / ఆధార్ కార్డ్ / ఇంటి పన్ను రసీదు / టెలిఫోన్ బిల్లు / విద్యుత్ బిల్లు."
  },
  "doc_id_address_alt": {
    name: "Aadhaar Card OR Voter ID Card OR Ration Card",
    name_te: "ఆధార్ కార్డ్ / ఓటరు ఐడి / రేషన్ కార్డ్ (ఏదైనా ఒకటి)",
    icon: "🪪",
    description: "Accepted identity/address proof: Upload any one of Aadhaar Card, Voter ID Card, or Ration Card.",
    description_te: "గుర్తింపు / చిరునామా రుజువు: ఆధార్ కార్డ్, ఓటరు ఐడి లేదా రేషన్ కార్డులలో ఏదైనా ఒక పత్రం అప్‌లోడ్ చేయండి."
  },
  "doc_poi": {
    name: "Proof of Identity (POI)",
    name_te: "గుర్తింపు రుజువు (POI)",
    icon: "👤",
    description: "One approved Proof of Identity document: Aadhaar Card, Voter ID, PAN Card, or Passport.",
    description_te: "అధికారిక గుర్తింపు రుజువు పత్రం: ఆధార్, పాన్, ఓటరు ఐడి లేదా పాస్‌పోర్ట్."
  },
  "doc_app_form": {
    name: "Application Form",
    name_te: "దరఖాస్తు ఫారమ్",
    icon: "📝",
    description: "Duly signed official service application form prescribed by the respective government department.",
    description_te: "సంబంధిత ప్రభుత్వ శాఖ నిర్దేశించిన సంతకం చేసిన అధికారిక దరఖాస్తు ఫారమ్."
  },
  "doc_medical_record": {
    name: "Doctor's Certificate / Medical Record",
    name_te: "వైద్య ధృవీకరణ పత్రం / ఆసుపత్రి రికార్డు",
    icon: "🏥",
    description: "Doctor's Certificate / Medical Record issued by a recognised medical authority.",
    description_te: "గుర్తింపు పొందిన ఆసుపత్రి లేదా వైద్య అధికారి జారీ చేసిన జనన వైద్య ధృవీకరణ పత్రం."
  },
  "doc_non_avail_cert": {
    name: "Non-Availability Certificate (NAC)",
    name_te: "నాన్-అవైలబిలిటీ సర్టిఫికేట్ (NAC)",
    icon: "📑",
    description: "Non-Availability Certificate from Gram Panchayat / Municipal Administration.",
    description_te: "గ్రామ పంచాయతీ లేదా మున్సిపల్ కార్యాలయం జారీ చేసిన నాన్-అవైలబిలిటీ సర్టిఫికేట్ (NAC)."
  },
  "doc_self_affidavit": {
    name: "Self-Affidavit",
    name_te: "స్వీయ ప్రమాణ పత్రం (అఫిడవిట్)",
    icon: "⚖️",
    description: "Notarized self-affidavit affirming date of birth, place of birth, or reason on stamp paper.",
    description_te: "నోటరీ ద్వారా ధృవీకరించబడిన స్టాంప్ పేపర్‌పై స్వీయ ప్రమాణ పత్రం (అఫిడవిట్)."
  },
  "doc_death_cert": {
    name: "Death Certificate",
    name_te: "మరణ ధృవీకరణ పత్రం",
    icon: "🕊️",
    description: "Official Death Certificate issued by Municipal Corporation, Gram Panchayat, or Registrar of Deaths.",
    description_te: "మున్సిపల్ కార్పొరేషన్ లేదా పంచాయతీ జారీ చేసిన అధికారిక మరణ ధృవీకరణ పత్రం."
  },
  "doc_marriage_cert": {
    name: "Marriage Certificate",
    name_te: "వివాహ ధృవీకరణ పత్రం",
    icon: "💍",
    description: "Official Marriage Certificate issued by Sub-Registrar / Municipal Registrar for spouse addition.",
    description_te: "సబ్-రిజిస్ట్రార్ కార్యాలయం జారీ చేసిన వివాహ రిజిస్ట్రేషన్ పత్రం."
  },
  "doc_schedule_docs": {
    name: "Schedule I to IV Documents / Revenue Records",
    name_te: "షెడ్యూల్ I నుండి IV పత్రాలు / రెవెన్యూ రికార్డులు",
    icon: "📁",
    description: "Statutory Schedule I to IV inquiry reports, family tree verification, or Revenue Tahsildar records.",
    description_te: "చట్టబద్ధమైన షెడ్యూల్ I నుండి IV విచారణ నివేదికలు మరియు రెవెన్యూ రికార్డులు."
  },
  "doc_fir_report": {
    name: "Old/Mutilated Voter ID OR FIR/Police Report",
    name_te: "పాడైన ఓటరు ఐడి లేదా FIR/పోలీస్ నివేదిక",
    icon: "🚓",
    description: "Old/Mutilated Voter ID OR FIR/Police Report for replacement of lost/damaged EPIC.",
    description_te: "ఓటరు కార్డు రీప్లేస్‌మెంట్ కోసం పాడైన కార్డు లేదా పోలీస్ FIR నివేదిక."
  },
  "doc_nativity_cert": {
    name: "Nativity Certificate",
    name_te: "స్థానికత / నివాస ధృవీకరణ పత్రం",
    icon: "🏡",
    description: "Official Nativity / Residence Certificate issued by Tahsildar for scholarship and admission.",
    description_te: "స్కాలర్‌షిప్‌ల కోసం తహశీల్దార్ జారీ చేసిన స్థానికత / నివాస ధృవీకరణ పత్రం."
  },
  "doc_correction_proof": {
    name: "Supporting Document for Correction",
    name_te: "సవరణకు ఆధారమైన పత్రం",
    icon: "🔍",
    description: "Supporting document related to the specific correction requested (e.g. proof of corrected detail).",
    description_te: "దరఖాస్తులో సవరించదలిచిన వివరాలకు సంబంధించిన అధికారిక ఆధార పత్రం."
  }
};

// Sub-operations Mapping for Services With Detailed Workflows
const SERVICE_SUB_OPERATIONS = {
  "birth-certificate": {
    "new": [
      { id: "normal", label: "Normal Registration (within 1 yr)", label_te: "సాధారణ నమోదు (1 సంవత్సరంలోపు)" },
      { id: "late", label: "Late Registration (after 1 yr)", label_te: "ఆలస్య నమోదు (1 సంవత్సరం తర్వాత)" }
    ]
  },
  "aadhaar-card": {
    "update": [
      { id: "name", label: "Name Update", label_te: "పేరు మార్పు" },
      { id: "address", label: "Address Update", label_te: "చిరునామా మార్పు" },
      { id: "dob", label: "Date of Birth Update", label_te: "పుట్టిన తేదీ మార్పు" },
      { id: "gender", label: "Gender Update", label_te: "లింగ నిర్ధారణ మార్పు" },
      { id: "mobile_email", label: "Mobile / Email", label_te: "మొబైల్ / ఈమెయిల్" },
      { id: "biometrics", label: "Photo / Biometrics", label_te: "ఫోటో / బయోమెట్రిక్స్" },
      { id: "document_update", label: "POI / POA Document Update", label_te: "POI / POA పత్రాల అప్‌డేట్" }
    ]
  },
  "pan-card": {
    "update": [
      { id: "name", label: "Name Correction", label_te: "పేరు సవరణ" },
      { id: "dob", label: "DOB Correction", label_te: "పుట్టిన తేదీ సవరణ" },
      { id: "personal", label: "Other Personal Detail", label_te: "వ్యక్తిగత వివరాల సవరణ" },
      { id: "address", label: "Address / Contact Update", label_te: "చిరునామా / సంప్రదింపు" },
      { id: "reprint", label: "PAN Card Reprint", label_te: "పాన్ రీప్రింట్" }
    ]
  },
  "voter-id-card": {
    "update": [
      { id: "shifting", label: "Shifting of Residence", label_te: "నివాస మార్పు" },
      { id: "correction", label: "Correction of Entries", label_te: "వివరాల సవరణ" },
      { id: "photo", label: "Photograph Change", label_te: "ఫోటో మార్పు" },
      { id: "replacement", label: "Replacement of Lost/Damaged EPIC", label_te: "ఓటరు కార్డు రీప్లేస్‌మెంట్" }
    ]
  },
  "ration-card": {
    "update": [
      { id: "member_addition", label: "Member Addition", label_te: "సభ్యుల చేరిక" },
      { id: "member_deletion", label: "Member Deletion", label_te: "సభ్యుల తొలగింపు" },
      { id: "address_change", label: "Address Change", label_te: "చిరునామా మార్పు" },
      { id: "correction", label: "Details Correction", label_te: "వివరాల సవరణ" },
      { id: "splitting", label: "Ration Card Splitting", label_te: "కార్డు విభజన" },
      { id: "surrender", label: "Ration Card Surrender", label_te: "కార్డు రద్దు" }
    ]
  }
};

// Precise Service Document Requirements: New Application vs Update / Correction
const SERVICE_REQUIREMENTS_MAP = {
  // 1. INCOME CERTIFICATE
  "income-certificate": {
    new: [
      { docId: "doc_id_address_alt", isMandatory: true, badgeType: "alt" },
      { docId: "doc_salary_slip", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_app_form", isMandatory: true, badgeType: "mandatory" }
    ],
    update: [
      { docId: "doc_income_cert", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_correction_proof", isMandatory: true, badgeType: "mandatory" }
    ]
  },

  // 2. CASTE CERTIFICATE
  "caste-certificate": {
    new: [
      { docId: "doc_family_caste_cert", isMandatory: false, badgeType: "conditional" },
      { docId: "doc_tenth_memo", isMandatory: true, badgeType: "alt" },
      { docId: "doc_study_cert", isMandatory: true, badgeType: "alt" },
      { docId: "doc_id_address_alt", isMandatory: true, badgeType: "alt" },
      { docId: "doc_schedule_docs", isMandatory: false, badgeType: "conditional" },
      { docId: "doc_app_form", isMandatory: true, badgeType: "mandatory" }
    ],
    update: [
      { docId: "doc_caste_cert", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_correction_proof", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_family_caste_cert", isMandatory: false, badgeType: "conditional" }
    ]
  },

  // 3. BIRTH CERTIFICATE
  "birth-certificate": {
    new: {
      normal: [
        { docId: "doc_medical_record", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_app_form", isMandatory: true, badgeType: "mandatory" }
      ],
      late: [
        { docId: "doc_non_avail_cert", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_ration_card", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_tenth_memo", isMandatory: false, badgeType: "conditional" },
        { docId: "doc_self_affidavit", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_correction_proof", isMandatory: true, badgeType: "mandatory" }
      ]
    },
    update: [] // update / correction removed
  },

  // 4. AADHAAR CARD
  "aadhaar-card": {
    new: [
      { docId: "doc_poi", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_address_proof", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_birth_cert", isMandatory: false, badgeType: "conditional" }
    ],
    update: {
      name: [
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_poi", isMandatory: true, badgeType: "mandatory" }
      ],
      address: [
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_address_proof", isMandatory: true, badgeType: "mandatory" }
      ],
      dob: [
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_birth_cert", isMandatory: true, badgeType: "mandatory" }
      ],
      gender: [
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_correction_proof", isMandatory: false, badgeType: "conditional" }
      ],
      mobile_email: [
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" }
      ],
      biometrics: [
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" }
      ],
      document_update: [
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_poi", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_address_proof", isMandatory: true, badgeType: "mandatory" }
      ]
    }
  },

  // 5. PAN CARD
  "pan-card": {
    new: [
      { docId: "doc_poi", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_address_proof", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_birth_cert", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_passport_photo", isMandatory: true, badgeType: "mandatory" }
    ],
    update: {
      name: [
        { docId: "doc_pan", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_poi", isMandatory: true, badgeType: "mandatory" }
      ],
      dob: [
        { docId: "doc_pan", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_birth_cert", isMandatory: true, badgeType: "mandatory" }
      ],
      personal: [
        { docId: "doc_pan", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_correction_proof", isMandatory: true, badgeType: "mandatory" }
      ],
      address: [
        { docId: "doc_pan", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_address_proof", isMandatory: true, badgeType: "mandatory" }
      ],
      reprint: [
        { docId: "doc_pan", isMandatory: true, badgeType: "mandatory" }
      ]
    }
  },

  // 6. VOTER ID CARD
  "voter-id-card": {
    new: [
      { docId: "doc_passport_photo", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_birth_cert", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_address_proof", isMandatory: true, badgeType: "mandatory" }
    ],
    update: {
      shifting: [
        { docId: "doc_voter_id", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_address_proof", isMandatory: true, badgeType: "mandatory" }
      ],
      correction: [
        { docId: "doc_voter_id", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_correction_proof", isMandatory: true, badgeType: "mandatory" }
      ],
      photo: [
        { docId: "doc_voter_id", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_passport_photo", isMandatory: true, badgeType: "mandatory" }
      ],
      replacement: [
        { docId: "doc_voter_id", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_fir_report", isMandatory: true, badgeType: "mandatory" }
      ]
    }
  },

  // 7. SCHOLARSHIP APPLICATION (NEW ONLY)
  "scholarship-application": {
    new: [
      { docId: "doc_caste_cert", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_income_cert", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_ration_card", isMandatory: false, badgeType: "conditional" },
      { docId: "doc_tenth_memo", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_inter_memo", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_college_allotment", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_father_aadhaar", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_mother_aadhaar", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_bank_passbook", isMandatory: false, badgeType: "conditional" },
      { docId: "doc_passport_photo", isMandatory: false, badgeType: "conditional" }
    ],
    update: [] // No Update option
  },

  // 8. RATION CARD
  "ration-card": {
    new: [
      { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_address_proof", isMandatory: true, badgeType: "mandatory" },
      { docId: "doc_income_cert", isMandatory: true, badgeType: "mandatory" }
    ],
    update: {
      member_addition: [
        { docId: "doc_ration_card", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" }
      ],
      member_deletion: [
        { docId: "doc_ration_card", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_correction_proof", isMandatory: false, badgeType: "conditional" }
      ],
      address_change: [
        { docId: "doc_ration_card", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_address_proof", isMandatory: true, badgeType: "mandatory" }
      ],
      correction: [
        { docId: "doc_ration_card", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_correction_proof", isMandatory: true, badgeType: "mandatory" }
      ],
      splitting: [
        { docId: "doc_ration_card", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_address_proof", isMandatory: false, badgeType: "conditional" }
      ],
      surrender: [
        { docId: "doc_ration_card", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_aadhaar", isMandatory: true, badgeType: "mandatory" },
        { docId: "doc_correction_proof", isMandatory: true, badgeType: "mandatory" }
      ]
    }
  },

  // 9. OVERVIEW (When selection is cleared)
  "all-categories": [
    { docId: "doc_aadhaar", isMandatory: false, badgeType: "optional" },
    { docId: "doc_pan", isMandatory: false, badgeType: "optional" },
    { docId: "doc_voter_id", isMandatory: false, badgeType: "optional" },
    { docId: "doc_caste_cert", isMandatory: false, badgeType: "optional" },
    { docId: "doc_income_cert", isMandatory: false, badgeType: "optional" },
    { docId: "doc_bank_passbook", isMandatory: false, badgeType: "optional" },
    { docId: "doc_passport_photo", isMandatory: false, badgeType: "optional" },
    { docId: "doc_ration_card", isMandatory: false, badgeType: "optional" },
    { docId: "doc_study_cert", isMandatory: false, badgeType: "optional" },
    { docId: "doc_tenth_memo", isMandatory: false, badgeType: "optional" },
    { docId: "doc_inter_memo", isMandatory: false, badgeType: "optional" },
    { docId: "doc_father_aadhaar", isMandatory: false, badgeType: "optional" },
    { docId: "doc_mother_aadhaar", isMandatory: false, badgeType: "optional" },
    { docId: "doc_birth_cert", isMandatory: false, badgeType: "optional" },
    { docId: "doc_college_allotment", isMandatory: false, badgeType: "optional" },
    { docId: "doc_salary_slip", isMandatory: false, badgeType: "optional" },
    { docId: "doc_family_caste_cert", isMandatory: false, badgeType: "optional" },
    { docId: "doc_address_proof", isMandatory: false, badgeType: "optional" }
  ]
};

document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const paramService = urlParams.get("service");
  const paramType = urlParams.get("type");

  if (paramType === "update") {
    currentApplicationType = "update";
  } else {
    currentApplicationType = "new";
  }

  // Initialize Search Bar, Dropdown, and Event Listeners
  initServiceSearchDropdown();

  // Explicit UI Flow:
  // - When the page initially loads and the search bar is empty, display ALL existing 18 document categories.
  // - Do not automatically select any government service unless explicitly passed in the URL.
  if (paramService) {
    const matched = OFFICIAL_SERVICES.find(s => s.slug === paramService || s.id === paramService);
    if (matched) {
      selectGovernmentService(matched.slug, currentApplicationType, false);
    } else {
      clearServiceSelection();
    }
  } else {
    // Default state = Show ALL documents and keep search bar empty
    clearServiceSelection();
  }

  const runVerificationBtn = document.getElementById("btn-start-verification");
  if (runVerificationBtn) {
    runVerificationBtn.addEventListener("click", triggerVerificationPipeline);
  }
});

/**
 * Initialize Service Search Bar and Dropdown Functionality
 */
function initServiceSearchDropdown() {
  const searchInput = document.getElementById("service-search-input");
  const dropdownBtn = document.getElementById("btn-toggle-service-dropdown");
  const dropdownMenu = document.getElementById("service-dropdown-menu");
  const clearBtn = document.getElementById("btn-clear-service");

  if (!searchInput || !dropdownMenu) return;

  // Render items into dropdown
  renderDropdownItems(OFFICIAL_SERVICES);

  // Clicking the search bar should open the Government Services dropdown
  searchInput.addEventListener("click", () => {
    openDropdown();
  });

  // Focus on input opens dropdown
  searchInput.addEventListener("focus", () => {
    openDropdown();
  });

  // Search input typing filter
  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (clearBtn) {
      clearBtn.style.display = query.length > 0 ? "flex" : "none";
    }
    if (query.length === 0 && currentService) {
      // User cleared input: immediately restore ALL original document categories
      clearServiceSelection();
      openDropdown();
      return;
    }
    const filtered = OFFICIAL_SERVICES.filter(srv => {
      const matchName = srv.name.toLowerCase().includes(query);
      const matchNameTe = (srv.name_te || "").toLowerCase().includes(query);
      const matchDept = (srv.department || "").toLowerCase().includes(query);
      return matchName || matchNameTe || matchDept;
    });
    renderDropdownItems(filtered);
    openDropdown();
  });

  // Toggle button click
  if (dropdownBtn) {
    dropdownBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleDropdown();
    });
  }

  // Close dropdown when clicking outside
  document.addEventListener("click", (e) => {
    const section = document.getElementById("service-selection-section");
    if (section && !section.contains(e.target)) {
      closeDropdown();
    }
  });

  // Keyboard navigation: Escape key closes
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeDropdown();
    }
  });
}

function openDropdown() {
  const dropdownMenu = document.getElementById("service-dropdown-menu");
  const dropdownBtn = document.getElementById("btn-toggle-service-dropdown");
  if (dropdownMenu) {
    dropdownMenu.style.display = "block";
  }
  if (dropdownBtn) {
    dropdownBtn.classList.add("open");
    dropdownBtn.setAttribute("aria-expanded", "true");
  }
}

function closeDropdown() {
  const dropdownMenu = document.getElementById("service-dropdown-menu");
  const dropdownBtn = document.getElementById("btn-toggle-service-dropdown");
  if (dropdownMenu) {
    dropdownMenu.style.display = "none";
  }
  if (dropdownBtn) {
    dropdownBtn.classList.remove("open");
    dropdownBtn.setAttribute("aria-expanded", "false");
  }
}

function toggleDropdown() {
  const dropdownMenu = document.getElementById("service-dropdown-menu");
  if (dropdownMenu && dropdownMenu.style.display === "block") {
    closeDropdown();
  } else {
    openDropdown();
  }
}

/**
 * Render items in the Government Services Dropdown Menu
 */
function renderDropdownItems(servicesList) {
  const dropdownMenu = document.getElementById("service-dropdown-menu");
  if (!dropdownMenu) return;

  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  if (!servicesList || servicesList.length === 0) {
    dropdownMenu.innerHTML = `
      <li style="padding: 14px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">
        No government services found matching your search.
      </li>
    `;
    return;
  }

  dropdownMenu.innerHTML = servicesList.map(srv => {
    const isSelected = srv.slug === currentServiceSlug;
    const displayName = isTe ? (srv.name_te || srv.name) : srv.name;
    const deptName = isTe ? (srv.department_te || srv.department) : srv.department;
    const subTitle = isTe ? srv.name : (srv.name_te || "");

    return `
      <li 
        class="service-dropdown-item ${isSelected ? 'active' : ''}" 
        onclick="selectGovernmentService('${srv.slug}', '${currentApplicationType}', true)"
        role="option"
        aria-selected="${isSelected}"
      >
        <div class="service-item-title">
          <span class="service-item-icon">${srv.icon || '🏛️'}</span>
          <div>
            <div>${escapeHtml(displayName)}</div>
            <div class="service-item-dept">${escapeHtml(deptName)} ${subTitle ? `• <span style="opacity: 0.85;">${escapeHtml(subTitle)}</span>` : ''}</div>
          </div>
        </div>
        <div>
          <span class="service-item-badge">${srv.has_update ? 'New / Update' : 'New Only'}</span>
        </div>
      </li>
    `;
  }).join("");
}

/**
 * Handle Government Service Selection
 */
async function selectGovernmentService(slug, appType = "new", fromUserClick = false) {
  const matchedSrv = OFFICIAL_SERVICES.find(s => s.slug === slug || s.id === slug) || OFFICIAL_SERVICES[0];
  currentService = matchedSrv;
  currentServiceSlug = matchedSrv.slug;

  // Handle application type constraints (e.g. Scholarship has no update)
  if (!matchedSrv.has_update) {
    currentApplicationType = "new";
  } else {
    currentApplicationType = (appType === "update") ? "update" : "new";
  }

  // Update search input text
  const searchInput = document.getElementById("service-search-input");
  const clearBtn = document.getElementById("btn-clear-service");
  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  if (searchInput) {
    searchInput.value = isTe ? (matchedSrv.name_te || matchedSrv.name) : matchedSrv.name;
  }
  if (clearBtn) {
    clearBtn.style.display = "flex";
  }

  // Update dropdown items active state and close dropdown
  renderDropdownItems(OFFICIAL_SERVICES);
  closeDropdown();

  // Update Application Type bar controls & visibility
  updateApplicationTypeControls(matchedSrv);

  // Update Sub-operation selector controls
  updateSubOperationControls(matchedSrv, currentApplicationType);

  // Clear uploaded files map when switching service from user interaction to keep sessions clean
  if (fromUserClick) {
    uploadedFilesMap = {};
    activeSessionId = SessionStore.createNewSession();
  } else if (!activeSessionId) {
    activeSessionId = SessionStore.createNewSession();
  }
  sessionStorage.setItem('active_service_id', matchedSrv.id);
  sessionStorage.setItem('active_service_slug', matchedSrv.slug);
  sessionStorage.setItem('active_app_type', currentApplicationType);

  // Load and render relevant documents for this specific service & application type
  await loadDocumentsForSelection(matchedSrv.slug, currentApplicationType, currentSubOperation);
}

/**
 * Clear Service Selection and Restore Original Document Categories
 */
function clearServiceSelection() {
  currentService = null;
  currentServiceSlug = null;
  currentApplicationType = "all";
  currentSubOperation = "";
  uploadedFilesMap = {};
  activeSessionId = SessionStore.createNewSession();

  const searchInput = document.getElementById("service-search-input");
  const clearBtn = document.getElementById("btn-clear-service");
  const subOpBar = document.getElementById("sub-operation-bar");
  const appTypeControls = document.getElementById("app-type-controls") || document.querySelector(".app-type-controls");
  const activeText = document.getElementById("active-service-text");
  const serviceTitleEl = document.getElementById("service-title");
  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  if (searchInput) {
    searchInput.value = "";
  }
  if (clearBtn) {
    clearBtn.style.display = "none";
  }
  if (appTypeControls) {
    appTypeControls.style.display = "none";
  }
  if (subOpBar) {
    subOpBar.style.display = "none";
  }
  if (activeText) {
    activeText.textContent = isTe ? "అన్ని ప్రభుత్వ పత్రాల వర్గాలు" : "All Government Document Categories";
  }
  if (serviceTitleEl) {
    serviceTitleEl.textContent = isTe ? "ప్రభుత్వ పత్రాల పరిశీలన" : "Government Document Verification";
  }

  sessionStorage.removeItem('active_service_id');
  sessionStorage.removeItem('active_service_slug');
  sessionStorage.removeItem('active_app_type');

  renderDropdownItems(OFFICIAL_SERVICES);

  // Immediately restore ALL original document categories and upload cards
  loadOverviewDocumentCategories();
}

/**
 * Handle Application Option Selection (New vs Update)
 */
function selectApplicationType(type) {
  if (type === "update" && currentService && !currentService.has_update) {
    return; // Service does not support update
  }

  currentApplicationType = type;
  sessionStorage.setItem('active_app_type', currentApplicationType);

  // Clear uploads for clean switch
  uploadedFilesMap = {};
  activeSessionId = SessionStore.createNewSession();

  updateApplicationTypeControls(currentService);
  updateSubOperationControls(currentService, currentApplicationType);
  loadDocumentsForSelection(currentServiceSlug, currentApplicationType, currentSubOperation);
}

/**
 * Handle Sub-Operation Selection (e.g. Normal vs Late, or specific Update target)
 */
function selectSubOperation(subOpId) {
  currentSubOperation = subOpId;
  uploadedFilesMap = {};
  activeSessionId = SessionStore.createNewSession();

  // Update active pill in sub-op buttons
  const subOpButtons = document.querySelectorAll(".sub-op-btn");
  subOpButtons.forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-sub-op") === subOpId);
  });

  loadDocumentsForSelection(currentServiceSlug, currentApplicationType, currentSubOperation);
}

/**
 * Update UI for Application Type Buttons and Active Badge
 */
function updateApplicationTypeControls(srv) {
  const btnNew = document.getElementById("btn-type-new");
  const btnUpdate = document.getElementById("btn-type-update");
  const appTypeControls = document.getElementById("app-type-controls") || document.querySelector(".app-type-controls");
  const activeText = document.getElementById("active-service-text");
  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  if (!srv) {
    if (appTypeControls) appTypeControls.style.display = "none";
    return;
  }

  // Show application type controls once a service is selected
  if (appTypeControls) {
    appTypeControls.style.display = "flex";
  }

  // Toggle button active states
  if (btnNew) {
    btnNew.classList.toggle("active", currentApplicationType === "new");
  }

  if (btnUpdate) {
    if (!srv.has_update) {
      btnUpdate.style.display = "none";
    } else {
      btnUpdate.style.display = "inline-flex";
      btnUpdate.classList.toggle("active", currentApplicationType === "update");
    }
  }

  // Update active status pill
  if (activeText) {
    const srvName = isTe ? (srv.name_te || srv.name) : srv.name;
    const typeLabel = (currentApplicationType === "update") 
      ? (isTe ? "సవరణ / అప్‌డేట్" : "Update / Correction") 
      : (isTe ? "కొత్త దరఖాస్తు" : "New Application");
    activeText.textContent = `${srvName} • ${typeLabel}`;
  }
}

/**
 * Render Sub-Operation controls if service and application type have sub-options
 */
function updateSubOperationControls(srv, appType) {
  const subOpBar = document.getElementById("sub-operation-bar");
  const subOpButtonsContainer = document.getElementById("sub-op-buttons");
  const subOpLabel = document.getElementById("sub-op-label");
  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  if (!subOpBar || !subOpButtonsContainer) return;

  if (!srv) {
    subOpBar.style.display = "none";
    currentSubOperation = "";
    return;
  }

  const subOps = (SERVICE_SUB_OPERATIONS[srv.slug] && SERVICE_SUB_OPERATIONS[srv.slug][appType]) || [];

  if (subOps.length === 0) {
    subOpBar.style.display = "none";
    currentSubOperation = "";
    return;
  }

  // Set default sub-operation if not already valid
  if (!subOps.some(o => o.id === currentSubOperation)) {
    currentSubOperation = subOps[0].id;
  }

  subOpBar.style.display = "flex";

  if (subOpLabel) {
    if (srv.slug === "birth-certificate") {
      subOpLabel.textContent = isTe ? "నమోదు రకం:" : "Registration Type:";
    } else if (srv.slug === "aadhaar-card") {
      subOpLabel.textContent = isTe ? "అప్‌డేట్ వివరాలు:" : "Select Update Detail:";
    } else if (srv.slug === "pan-card") {
      subOpLabel.textContent = isTe ? "సవరణ అంశం:" : "Correction / Request:";
    } else if (srv.slug === "voter-id-card") {
      subOpLabel.textContent = isTe ? "ఫారం 8 సేవ:" : "Form 8 Service:";
    } else if (srv.slug === "ration-card") {
      subOpLabel.textContent = isTe ? "రేషన్ కార్డు సేవ:" : "Select Operation:";
    } else {
      subOpLabel.textContent = isTe ? "ఎంపిక:" : "Select Option:";
    }
  }

  subOpButtonsContainer.innerHTML = subOps.map(op => {
    const isActive = op.id === currentSubOperation;
    const label = isTe ? (op.label_te || op.label) : op.label;
    return `
      <button 
        type="button" 
        class="sub-op-btn ${isActive ? 'active' : ''}" 
        data-sub-op="${op.id}" 
        onclick="selectSubOperation('${op.id}')"
      >
        ${escapeHtml(label)}
      </button>
    `;
  }).join("");
}

/**
 * Fetch and Render Documents for the Selected Service, Option, and Sub-Operation
 */
async function loadDocumentsForSelection(slug, appType, subOp = "") {
  const uploadGridEl = document.getElementById("upload-cards-grid");
  const serviceTitleEl = document.getElementById("service-title");
  if (!uploadGridEl) return;

  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  // Show subtle loading state
  uploadGridEl.innerHTML = `
    <div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
      <p style="color: var(--text-muted); font-size: 1rem;">${isTe ? 'పత్రాల అవసరాలను సేకరిస్తోంది...' : 'Loading relevant document requirements...'}</p>
    </div>
  `;

  let docsList = [];

  try {
    let url = `${API_BASE}/services/${slug}/documents?type=${appType}`;
    if (subOp) url += `&sub_operation=${encodeURIComponent(subOp)}`;

    const resp = await fetch(url);
    if (resp.ok) {
      const data = await resp.json();
      if (data.documents && data.documents.length > 0) {
        docsList = data.documents;
      }
    }
  } catch (err) {
    // Fallback to client catalog
  }

  // If backend returned empty or was unreachable, use the exact local requirements map
  if (!docsList || docsList.length === 0) {
    const serviceReqs = SERVICE_REQUIREMENTS_MAP[slug];
    let reqs = [];
    if (serviceReqs) {
      const typeReqs = serviceReqs[appType];
      if (Array.isArray(typeReqs)) {
        reqs = typeReqs;
      } else if (typeReqs && typeof typeReqs === "object") {
        reqs = typeReqs[subOp] || Object.values(typeReqs)[0] || [];
      }
    }

    docsList = reqs.map((item, idx) => {
      const def = DOCUMENT_DEFINITIONS[item.docId] || { name: item.docId, name_te: item.docId, icon: "📄", description: "" };
      return {
        document_id: item.docId,
        name: def.name,
        name_te: def.name_te,
        description: def.description,
        description_te: def.description_te,
        icon: def.icon,
        is_mandatory: item.isMandatory,
        badge_type: item.badgeType || (item.isMandatory ? "mandatory" : "optional"),
        display_order: idx + 1
      };
    });
  }

  requiredDocuments = docsList;

  // Update Page Title if present
  if (serviceTitleEl && currentService) {
    const srvName = isTe ? (currentService.name_te || currentService.name) : currentService.name;
    const typeLabel = (currentApplicationType === "update") 
      ? (isTe ? "సవరణ / అప్‌డేట్" : "Update") 
      : (isTe ? "కొత్త దరఖాస్తు" : "New Application");
    serviceTitleEl.textContent = `${srvName} (${typeLabel})`;
  }

  // Render cards
  renderUploadCards(uploadGridEl, activeSessionId);
  updateUploadCounter();
}

/**
 * Load Original Master Document Categories Overview (When Selection is Cleared)
 */
function loadOverviewDocumentCategories() {
  const uploadGridEl = document.getElementById("upload-cards-grid");
  if (!uploadGridEl) return;

  const rawList = SERVICE_REQUIREMENTS_MAP["all-categories"] || [];
  requiredDocuments = rawList.map((item, idx) => {
    const def = DOCUMENT_DEFINITIONS[item.docId] || { name: item.docId, name_te: item.docId, icon: "📄", description: "" };
    return {
      document_id: item.docId,
      name: def.name,
      name_te: def.name_te,
      description: def.description,
      description_te: def.description_te,
      icon: def.icon,
      is_mandatory: item.isMandatory,
      badge_type: item.badgeType || "optional",
      display_order: idx + 1
    };
  });

  renderUploadCards(uploadGridEl, activeSessionId);
  updateUploadCounter();
}

/**
 * Render Upload Cards Grid for Relevant Documents Only
 */
function renderUploadCards(container, sessionId) {
  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  if (!requiredDocuments || requiredDocuments.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; background: var(--bg-card); border: 2px dashed #CBD5E1; border-radius: 12px; padding: 3rem 1.5rem; text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏛️</div>
        <h3 style="color: var(--accent-navy); margin-bottom: 0.5rem;">Select a Government Service Above</h3>
        <p style="color: var(--text-muted); max-width: 500px; margin: 0 auto;">
          Choose one of the 8 available government services and select New Application or Update to view the required documents.
        </p>
      </div>
    `;
    return;
  }

  container.innerHTML = requiredDocuments.map((doc) => {
    const docName = isTe ? (doc.name_te || doc.name) : doc.name;
    const docDesc = isTe ? (doc.description_te || doc.description) : doc.description;
    const uploadBtnText = (typeof t === 'function') ? t("btn_select_upload") : "📤 Select & Upload File";
    const formatsNote = (typeof t === 'function') ? t("upload_formats_note") : "Formats: PDF, JPG, PNG (Max 8 MB)";

    // Distinct Badge Display based on requirement rule
    let badgeHtml = "";
    if (doc.badge_type === "alt") {
      badgeHtml = `<span class="doc-badge-alt">${isTe ? 'ఏదైనా ఒకటి అప్‌లోడ్ చేయండి' : 'Upload Any One'}</span>`;
    } else if (doc.badge_type === "conditional") {
      badgeHtml = `<span class="doc-badge-conditional">${isTe ? 'వర్తిస్తేనే అవసరం' : 'Required only if applicable'}</span>`;
    } else if (doc.is_mandatory) {
      badgeHtml = `<span class="doc-badge-mandatory">${isTe ? 'తప్పనిసరి *' : 'Required *'}</span>`;
    } else {
      badgeHtml = `<span class="doc-badge-optional">${isTe ? 'ఐచ్ఛికం' : 'Optional'}</span>`;
    }

    return `
      <div class="upload-card" id="card-${doc.document_id}">
        <!-- File input element -->
        <input 
          type="file" 
          id="file-input-${doc.document_id}" 
          accept=".pdf,.jpg,.jpeg,.png" 
          style="display: none;" 
          onchange="handleFileSelect('${doc.document_id}', '${sessionId}')"
        >
        
        <div style="display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 0.75rem;">
          <div class="upload-icon">${doc.icon || '📄'}</div>
          <div>${badgeHtml}</div>
        </div>

        <h4 style="margin-bottom: 0.35rem; color: var(--accent-navy); font-size: 1.05rem;">
          ${escapeHtml(docName)}${doc.is_mandatory ? ' <span class="required-asterisk" style="color: #15803D; font-weight: 800;">*</span>' : ''}
        </h4>

        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.25rem; line-height: 1.45;">
          ${escapeHtml(docDesc)}
        </p>

        <div id="status-area-${doc.document_id}">
          <button type="button" class="btn-secondary" onclick="triggerFilePicker('${doc.document_id}')" style="width: 100%;">
            ${escapeHtml(uploadBtnText)}
          </button>
          <p class="upload-status-note">${escapeHtml(formatsNote)}</p>
        </div>

        <div id="progress-area-${doc.document_id}" style="display: none; margin-top: 1rem;">
          <div style="background: #E2E8F0; height: 6px; border-radius: 3px; overflow: hidden;">
            <div id="progress-bar-${doc.document_id}" style="background: var(--accent-saffron); width: 0%; height: 100%; transition: width 0.3s;"></div>
          </div>
          <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
            ${isTe ? 'అప్‌లోడ్ అవుతోంది...' : 'Uploading...'}
          </p>
        </div>

        <div id="feedback-${doc.document_id}" style="margin-top: 0.75rem;"></div>
      </div>
    `;
  }).join("");
}

function updateUploadCounter() {
  const counterEl = document.getElementById("upload-counter");
  if (!counterEl) return;

  const count = Object.keys(uploadedFilesMap).length;
  const total = requiredDocuments.length || 0;
  const mandatoryCount = requiredDocuments.filter(d => d.is_mandatory).length;
  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  if (!currentService) {
    if (isTe) {
      counterEl.textContent = `📂 ${count} / ${total} పత్రాలు అప్‌లోడ్ చేయబడ్డాయి`;
    } else {
      counterEl.textContent = `📂 ${count} of ${total} Documents Uploaded`;
    }
  } else {
    if (isTe) {
      counterEl.textContent = `📂 ${count} / ${total} పత్రాలు (${mandatoryCount} తప్పనిసరి)`;
    } else {
      counterEl.textContent = `📂 ${count} of ${total} Documents Uploaded (${mandatoryCount} Required)`;
    }
  }
}

function triggerFilePicker(documentId) {
  let fileInput = document.getElementById(`file-input-${documentId}`);
  if (!fileInput) {
    fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.id = `file-input-${documentId}`;
    fileInput.accept = ".pdf,.jpg,.jpeg,.png";
    fileInput.style.display = "none";
    const curSessionId = activeSessionId || SessionStore.getSessionId() || SessionStore.createNewSession();
    fileInput.onchange = () => handleFileSelect(documentId, curSessionId);
    const cardEl = document.getElementById(`card-${documentId}`) || document.body;
    cardEl.appendChild(fileInput);
  }
  fileInput.value = "";
  fileInput.click();
}

async function handleFileSelect(documentId, sessionId) {
  const fileInput = document.getElementById(`file-input-${documentId}`);
  const feedbackEl = document.getElementById(`feedback-${documentId}`);
  const progressArea = document.getElementById(`progress-area-${documentId}`);
  const progressBar = document.getElementById(`progress-bar-${documentId}`);
  const cardEl = document.getElementById(`card-${documentId}`);
  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  if (!fileInput || !fileInput.files || fileInput.files.length === 0) return;

  const file = fileInput.files[0];

  // Client side format validation
  const ext = file.name.split('.').pop().toLowerCase();
  const allowed = ['pdf', 'jpg', 'jpeg', 'png'];
  if (!allowed.includes(ext)) {
    const errText = isTe 
      ? "అసంమతమైన ఫైల్ ఫార్మాట్. దయచేసి PDF, JPG, JPEG, లేదా PNG ను మాత్రమే అప్‌లోడ్ చేయండి." 
      : "Unsupported file format. Please upload PDF, JPG, JPEG, or PNG.";
    feedbackEl.innerHTML = `<div class="alert alert-danger" style="margin-top: 8px;">${errText}</div>`;
    return;
  }

  // Size validation: max 8MB
  if (file.size > 8 * 1024 * 1024) {
    const errText = isTe 
      ? "ఫైల్ పరిమాణం 8 MB ని మించిపోయింది." 
      : `File size (${(file.size/(1024*1024)).toFixed(2)} MB) exceeds max limit of 8 MB.`;
    feedbackEl.innerHTML = `<div class="alert alert-danger" style="margin-top: 8px;">${errText}</div>`;
    return;
  }

  progressArea.style.display = "block";
  progressBar.style.width = "40%";

  const srvId = currentService ? currentService.id : "srv_gov_doc_verify";
  const validSessionId = activeSessionId || (sessionId && sessionId !== 'null' && sessionId !== 'undefined' ? sessionId : null) || SessionStore.getSessionId() || SessionStore.createNewSession();
  activeSessionId = validSessionId;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("service_id", srvId);
  formData.append("document_id", documentId);
  formData.append("session_id", validSessionId);

  try {
    const token = AuthStore.getToken();
    const headers = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    progressBar.style.width = "75%";

    const resp = await fetch(`${API_BASE}/uploads`, {
      method: "POST",
      headers: headers,
      body: formData
    });

    progressBar.style.width = "100%";
    setTimeout(() => { progressArea.style.display = "none"; }, 350);

    const data = await resp.json();

    if (!resp.ok) {
      feedbackEl.innerHTML = `<div class="alert alert-danger" style="margin-top: 8px;">${escapeHtml(data.error || 'Upload failed.')}</div>`;
      return;
    }

    uploadedFilesMap[documentId] = data.upload;
    cardEl.classList.add("has-file");
    updateUploadCounter();

    const statusNote = isTe 
      ? "ℹ️ ఫైల్ అప్‌లోడ్ చేయబడింది. ధృవీకరణ సమయంలో పత్రం రకం పరిశీలించబడుతుంది." 
      : "ℹ️ File uploaded. Document type will be checked during verification.";
    const btnReplaceText = isTe ? "మార్చండి (Replace)" : "Replace";
    const btnRemoveText = isTe ? "తొలగించండి (Remove)" : "Remove";

    document.getElementById(`status-area-${documentId}`).innerHTML = `
      <div style="background-color: var(--accent-saffron-light); border: 1px solid var(--accent-saffron-border); border-radius: var(--border-radius-sm); padding: 10px; margin-bottom: 8px; text-align: left;">
        <div style="font-weight: 700; color: #78350F; font-size: 0.9rem; word-break: break-all;">📎 ${escapeHtml(file.name)}</div>
        <div style="font-size: 0.8rem; color: #92400E;">Size: ${data.upload.file_size_mb} MB</div>
        <div style="font-size: 0.82rem; color: #B45309; margin-top: 6px; font-weight: 600;">
          ${escapeHtml(statusNote)}
        </div>
      </div>
      <div style="display: flex; gap: 8px;">
        <button type="button" class="btn-secondary" style="flex: 1; padding: 6px; font-size: 0.82rem;" onclick="triggerFilePicker('${documentId}')">${escapeHtml(btnReplaceText)}</button>
        <button type="button" class="btn-secondary" style="flex: 1; padding: 6px; font-size: 0.82rem; color: var(--danger);" onclick="removeUploadSlot('${documentId}', '${data.upload.upload_id}')">${escapeHtml(btnRemoveText)}</button>
      </div>
    `;

    feedbackEl.innerHTML = ``;

  } catch (err) {
    progressArea.style.display = "none";
    feedbackEl.innerHTML = `<div class="alert alert-danger" style="margin-top: 8px;">Network upload error.</div>`;
  }
}

async function removeUploadSlot(documentId, uploadId) {
  try {
    await fetch(`${API_BASE}/uploads/${uploadId}`, { method: "DELETE" });
  } catch (e) {}

  delete uploadedFilesMap[documentId];
  updateUploadCounter();

  const cardEl = document.getElementById(`card-${documentId}`);
  if (cardEl) cardEl.classList.remove("has-file");

  const fileInput = document.getElementById(`file-input-${documentId}`);
  if (fileInput) fileInput.value = "";

  const isTe = (typeof getLanguage === 'function') && getLanguage() === "te";
  const uploadBtnText = (typeof t === 'function') ? t("btn_select_upload") : "📤 Select & Upload File";
  const formatsNote = (typeof t === 'function') ? t("upload_formats_note") : "Formats: PDF, JPG, PNG (Max 8 MB)";

  document.getElementById(`status-area-${documentId}`).innerHTML = `
    <button type="button" class="btn-secondary" onclick="triggerFilePicker('${documentId}')" style="width: 100%;">
      ${escapeHtml(uploadBtnText)}
    </button>
    <p class="upload-status-note">${escapeHtml(formatsNote)}</p>
  `;
}

function triggerVerificationPipeline() {
  const sessionId = activeSessionId || SessionStore.createNewSession();
  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  // Ensure at least one file has been uploaded
  const uploadedCount = Object.keys(uploadedFilesMap).length;
  if (uploadedCount === 0) {
    alert(isTe 
      ? "దయచేసి ధృవీకరణ ప్రారంభించడానికి కనీసం ఒక పత్రాన్ని ఎంచుకుని అప్‌లోడ్ చేయండి." 
      : "Please select and upload at least one document before starting verification.");
    return;
  }

  // If a service is selected, use it; otherwise use the unified Government Document Verification service
  const serviceId = currentService ? currentService.id : "srv_gov_doc_verify";
  const appType = currentService ? currentApplicationType : "all";

  // Redirect to verification pipeline with session, service id, and application type
  let targetUrl = `verification.html?session_id=${encodeURIComponent(sessionId)}&service_id=${encodeURIComponent(serviceId)}&type=${encodeURIComponent(appType)}`;
  if (currentSubOperation) {
    targetUrl += `&sub_operation=${encodeURIComponent(currentSubOperation)}`;
  }
  window.location.href = targetUrl;
}

function escapeHtml(str) {
  return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
}
