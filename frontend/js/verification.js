document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get("session_id") || SessionStore.getSessionId();
  const serviceId = urlParams.get("service_id") || sessionStorage.getItem('active_service_id');
  const appType = urlParams.get("app_type") || urlParams.get("application_type") || sessionStorage.getItem('active_app_type') || "new";
  const viewOnly = urlParams.get("view_only") === "true";

  if (viewOnly) {
    loadExistingResults(sessionId);
  } else if (sessionId && serviceId) {
    executeVerification(sessionId, serviceId, appType);
  } else {
    document.getElementById("results-container").innerHTML = `
      <div class="alert alert-danger">No active verification session found. Please select a service and upload documents.</div>
    `;
  }
});

async function executeVerification(sessionId, serviceId, appType = "new") {
  const progressBox = document.getElementById("pipeline-progress-box");
  const resultsContainer = document.getElementById("results-container");

  if (progressBox) progressBox.style.display = "block";
  if (resultsContainer) resultsContainer.style.display = "none";

  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const s1Text = (lang === "te") ? "1. OpenCV నాణ్యత తనిఖీ: మసకబారడం & స్పష్టత విశ్లేషణ..." : "1. OpenCV Quality Check: Blur, Brightness & Clarity Analysis...";
  const s2Text = (lang === "te") ? "2. OCR వచన సేకరణ: పత్రంలోని వచనం రీడ్ అవుతుందా లేదా..." : "2. OCR Text Extraction: Testing document text readability...";
  const s3Text = (lang === "te") ? "3. AI పత్రం రకం ధృవీకరణ: ఎంచుకున్న పత్రం రకంతో సరిపోల్చుతోంది..." : "3. AI Document Type Verification: Verifying uploaded file against selected document...";

  // Simulate step progress animation for user experience
  await updateStepUI(1, s1Text);
  await delay(600);
  await updateStepUI(2, s2Text);
  await delay(600);
  await updateStepUI(3, s3Text);

  try {
    const token = AuthStore.getToken();
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const resp = await fetch(`${API_BASE}/verification/run`, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ session_id: sessionId, service_id: serviceId, application_type: appType })
    });

    const data = await resp.json();

    if (!resp.ok) {
      if (progressBox) progressBox.style.display = "none";
      if (resultsContainer) {
        resultsContainer.style.display = "block";
        resultsContainer.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error || 'Verification pipeline error.')}</div>`;
      }
      return;
    }

    if (progressBox) progressBox.style.display = "none";
    if (resultsContainer) resultsContainer.style.display = "block";

    renderReportAndResults(data.session, data.document_results);

  } catch (err) {
    if (progressBox) progressBox.style.display = "none";
    if (resultsContainer) {
      resultsContainer.style.display = "block";
      resultsContainer.innerHTML = `<div class="alert alert-danger">Connection error executing verification.</div>`;
    }
  }
}

async function loadExistingResults(sessionId) {
  const resultsContainer = document.getElementById("results-container");
  const progressBox = document.getElementById("pipeline-progress-box");

  if (progressBox) progressBox.style.display = "none";
  if (resultsContainer) resultsContainer.style.display = "block";

  try {
    const token = AuthStore.getToken();
    const headers = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const resp = await fetch(`${API_BASE}/verification/results/${sessionId}`, { headers });
    const data = await resp.json();

    if (!resp.ok) {
      resultsContainer.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error || 'Report not found.')}</div>`;
      return;
    }

    renderReportAndResults(data.session, data.document_results);
  } catch (e) {
    resultsContainer.innerHTML = `<div class="alert alert-danger">Error loading report.</div>`;
  }
}

function renderReportAndResults(session, results) {
  const container = document.getElementById("results-container");
  if (!container) return;

  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  const verifiedCount = results.filter(r => r.status === "verified" || r.status === "ready").length;
  const poorQualityCount = results.filter(r => r.status === "poor_quality").length;
  const invalidTypeCount = results.filter(r => r.status === "invalid_type" || r.status === "invalid" || r.status === "needs_review" || r.status === "needs_attention").length;
  const missingCount = results.filter(r => r.status === "missing").length;

  const isAllVerified = (verifiedCount === results.length && results.length > 0);
  const overallBadgeClass = isAllVerified ? "ready" : "needs_attention";
  const statusIcon = isAllVerified ? "✓" : "⚠";

  const reportBadgeText = isTe ? "ధృవీకరణ సెషన్ నివేదిక" : "Verification Session Report";
  const overallStatusLabel = isTe ?
    (isAllVerified ? "మొత్తం స్థితి: ధృవీకరించబడింది (VERIFIED)" : "మొత్తం స్థితి: చర్య అవసరం (ACTION REQUIRED)") :
    (isAllVerified ? "OVERALL STATUS: VERIFIED" : "OVERALL STATUS: ACTION REQUIRED");

  const summaryMsg = isTe ?
    (isAllVerified ? "అవసరమైన పత్రాలన్నీ స్పష్టంగా ఉన్నాయి మరియు ఎంచుకున్న పత్రాల రకంతో సరిగ్గా సరిపోలాయి." : "కొన్ని పత్రాలలో నాణ్యత లేదా రకం సమస్యలు ఉన్నాయి. దయచేసి క్రింద హైలైట్ చేసిన పత్రాలను సరిచూసుకోండి.") :
    (isAllVerified ? "All required documents are clear, readable, and match the selected document types." : "Some documents have quality issues, invalid types, or are missing. Please review and replace the highlighted documents.");

  const statTotalLabel = isTe ? "మొత్తం అవసరమైనవి" : "Total Required";
  const statVerifiedLabel = isTe ? "ధృవీకరించబడింది (Verified)" : "Verified";
  const statPoorLabel = isTe ? "నాణ్యత లోపం (Poor Quality)" : "Poor Quality";
  const statInvalidLabel = isTe ? "తప్పుడు పత్రం (Invalid Type)" : "Invalid Document Type";
  const statMissingLabel = isTe ? "లభ్యం కాలేదు (Missing)" : "Missing";

  const proceedBtnText = isTe ? "అధికారిక ప్రభుత్వ పోర్టల్‌కు వెళ్ళండి →" : "Proceed to Official Government Portal →";
  const actionReqText = isTe ? "🚫 చర్య అవసరం: పోర్టల్‌కు వెళ్లేముందు సమస్యలను పరిష్కరించండి" : "🚫 Action Required: Fix issues before proceeding to Official Portal";

  const docResultsHeading = isTe ? "పత్రాల వారిగా విశ్లేషణ ఫలితాలు" : "Document-Wise Verification Results";

  let html = `
    <!-- Final Verification Report Summary -->
    <div class="report-summary-box">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
        <div>
          <span style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-saffron); font-weight: 700; letter-spacing: 0.05em;">
            ${escapeHtml(reportBadgeText)}
          </span>
          <h2 style="font-size: 1.8rem; margin: 4px 0 8px 0;">${escapeHtml(session.service_name || 'Government Service')}</h2>
          <p style="color: var(--text-muted); font-size: 0.95rem;">${escapeHtml(summaryMsg)}</p>
        </div>
        <div>
          <div class="status-badge ${overallBadgeClass}" style="font-size: 1.1rem; padding: 8px 18px;">
            ${statusIcon} ${escapeHtml(overallStatusLabel)}
          </div>
        </div>
      </div>

      <div class="report-stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));">
        <div class="stat-tile">
          <div class="num">${results.length}</div>
          <div class="lbl">${escapeHtml(statTotalLabel)}</div>
        </div>
        <div class="stat-tile" style="border-left: 3px solid #10B981;">
          <div class="num" style="color: #10B981;">${verifiedCount}</div>
          <div class="lbl">${escapeHtml(statVerifiedLabel)}</div>
        </div>
        <div class="stat-tile" style="border-left: 3px solid #F59E0B;">
          <div class="num" style="color: #F59E0B;">${poorQualityCount}</div>
          <div class="lbl">${escapeHtml(statPoorLabel)}</div>
        </div>
        <div class="stat-tile" style="border-left: 3px solid #EF4444;">
          <div class="num" style="color: #EF4444;">${invalidTypeCount}</div>
          <div class="lbl">${escapeHtml(statInvalidLabel)}</div>
        </div>
        <div class="stat-tile" style="border-left: 3px solid #6B7280;">
          <div class="num" style="color: #6B7280;">${missingCount}</div>
          <div class="lbl">${escapeHtml(statMissingLabel)}</div>
        </div>
      </div>

      <div style="background-color: var(--accent-saffron-light); border: 1px solid var(--accent-saffron-border); padding: 12px 16px; border-radius: var(--border-radius-sm); font-size: 0.85rem; color: #78350F; margin: 1.5rem 0;">
        <strong>📢 ${isTe ? 'గమనిక:' : 'Mandatory Disclaimer:'}</strong> ${escapeHtml(isTe ? 'ఇది ప్రాథమిక పత్రాల నాణ్యత & రకం తనిఖీ మాత్రమే. ఇది చట్టపరమైన ప్రామాణికత లేదా అధికారిక ప్రభుత్వ ఆమోదాన్ని నిర్ధారించదు.' : 'This is a preliminary document quality and document type check. It does not confirm legal authenticity or official government approval.')}
      </div>

      <div style="margin-top: 1.5rem; text-align: right;">
        ${isAllVerified ? `
          <a href="${session.official_portal_url || '#'}" target="_blank" class="btn-primary" style="font-size: 1.05rem; padding: 1rem 2rem;">
            ${escapeHtml(proceedBtnText)}
          </a>
        ` : `
          <button class="btn-secondary" disabled style="opacity: 0.65; cursor: not-allowed;">
            ${escapeHtml(actionReqText)}
          </button>
        `}
      </div>
    </div>

    <!-- Document Quality & Type Verification Matrix Table -->
    <div class="step-card" style="margin-bottom: 1.5rem; padding: 1.25rem;">
      <h3 style="margin-bottom: 0.85rem; color: var(--primary); font-size: 1.15rem; display: flex; align-items: center; gap: 8px;">
        <span>📋</span> ${isTe ? 'పత్రం నాణ్యత & రకం ధృవీకరణ పట్టిక' : 'Document Quality & Type Verification Matrix'}
      </h3>
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.92rem;">
          <thead>
            <tr style="background: #F8FAFC; border-bottom: 2px solid #E2E8F0; text-align: left;">
              <th style="padding: 10px 14px; font-weight: 700; color: #1E293B;">${isTe ? 'అవసరమైన పత్రం (Required Document)' : 'Required Document'}</th>
              <th style="padding: 10px 14px; font-weight: 700; color: #1E293B;">${isTe ? 'గుర్తించబడిన పత్రం (Detected Document)' : 'Detected Document'}</th>
              <th style="padding: 10px 14px; font-weight: 700; color: #1E293B; text-align: center;">${isTe ? 'నాణ్యత తనిఖీ (Quality Check)' : 'Quality & Clarity Check'}</th>
              <th style="padding: 10px 14px; font-weight: 700; color: #1E293B; text-align: center;">${isTe ? 'పత్రం రకం (Type Match)' : 'Document Type Match'}</th>
              <th style="padding: 10px 14px; font-weight: 700; color: #1E293B; text-align: center;">${isTe ? 'ఫలితం (Status)' : 'Status'}</th>
              <th style="padding: 10px 14px; font-weight: 700; color: #1E293B; text-align: center;">${isTe ? 'చర్య (Action)' : 'Action'}</th>
            </tr>
          </thead>
          <tbody>
            ${results.map(r => {
              const reqName = r.document_name || 'Document';
              const detectedDocName = r.status === 'missing' ? (isTe ? 'పత్రం అప్‌లోడ్ చేయలేదు' : 'No Document Uploaded') : (r.detected_document || r.detected_name || 'Unidentified Document');

              const isMissing = (r.status === 'missing');
              const isVerified = (r.status === 'verified' || r.status === 'ready');
              const isPoorQuality = (r.status === 'poor_quality');
              const isInvalidType = (r.status === 'invalid_type' || r.status === 'invalid' || r.status === 'needs_review' || r.status === 'needs_attention');

              // Quality Column Badge
              let qualityBadge = '';
              if (isMissing) {
                qualityBadge = `<span style="color: #6B7280; font-size: 0.85rem;">-</span>`;
              } else if (isPoorQuality) {
                qualityBadge = `<span style="background: #FEF3C7; color: #B45309; font-weight: 600; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem;">⚠️ Blurry / Unclear</span>`;
              } else {
                qualityBadge = `<span style="background: #DEF7EC; color: #03543F; font-weight: 600; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem;">✅ Clear & Readable</span>`;
              }

              // Document Type Column Badge
              let typeBadge = '';
              if (isMissing) {
                typeBadge = `<span style="color: #6B7280; font-size: 0.85rem;">-</span>`;
              } else if (isInvalidType) {
                typeBadge = `<span style="background: #FDE8E8; color: #9B1C1C; font-weight: 600; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem;">❌ Type Mismatch</span>`;
              } else {
                typeBadge = `<span style="background: #DEF7EC; color: #03543F; font-weight: 600; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem;">✅ Type Matched</span>`;
              }

              // Result Status Badge (Only 3 statuses + Missing)
              let resultStatusBadge = '';
              if (isVerified) {
                resultStatusBadge = `<span style="background: #DEF7EC; color: #03543F; font-weight: 700; padding: 5px 14px; border-radius: 20px; display: inline-block;">✅ Verified</span>`;
              } else if (isPoorQuality) {
                resultStatusBadge = `<span style="background: #FEF3C7; color: #B45309; font-weight: 700; padding: 5px 14px; border-radius: 20px; display: inline-block;">⚠️ Poor Quality</span>`;
              } else if (isInvalidType) {
                resultStatusBadge = `<span style="background: #FDE8E8; color: #9B1C1C; font-weight: 700; padding: 5px 14px; border-radius: 20px; display: inline-block;">❌ Invalid Document Type</span>`;
              } else {
                resultStatusBadge = `<span style="background: #F3F4F6; color: #4B5563; font-weight: 700; padding: 5px 14px; border-radius: 20px; display: inline-block;">📁 Missing</span>`;
              }

              return `
                <tr style="border-bottom: 1px solid #E2E8F0;">
                  <td style="padding: 12px 14px; font-weight: 600; color: #0F172A;">${escapeHtml(reqName)}</td>
                  <td style="padding: 12px 14px; color: #334155;">
                    <div><strong>${escapeHtml(detectedDocName)}</strong></div>
                  </td>
                  <td style="padding: 12px 14px; text-align: center;">${qualityBadge}</td>
                  <td style="padding: 12px 14px; text-align: center;">${typeBadge}</td>
                  <td style="padding: 12px 14px; text-align: center;">${resultStatusBadge}</td>
                  <td style="padding: 12px 14px; text-align: center;">
                    ${isVerified ? `
                      <span style="color: #059669; font-weight: 600; font-size: 0.85rem;">Ready ✓</span>
                    ` : `
                      <button type="button" class="btn-secondary" style="font-size: 0.8rem; padding: 4px 10px; font-weight: 600;" onclick="replaceDocumentInVerification('${r.document_id}', '${escapeHtml(reqName)}')">
                        🔄 ${isTe ? 'మార్చండి' : 'Replace'}
                      </button>
                    `}
                  </td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Document-Wise Analysis Cards -->
    <h3 style="margin-bottom: 1rem;">${escapeHtml(docResultsHeading)}</h3>
    <div style="display: flex; flex-direction: column; gap: 1rem;">
      ${results.map(r => renderDocumentResultCard(r)).join("")}
    </div>
  `;

  container.innerHTML = html;
}

function renderDocumentResultCard(r) {
  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const isTe = (lang === "te");

  const status = (r.status || "needs_review").toLowerCase();

  let badgeIcon = "✅";
  let badgeText = isTe ? "ధృవీకరించబడింది (VERIFIED)" : "VERIFIED";
  let borderLeftColor = "var(--success)";
  let reasonStyle = "background-color: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46;";

  if (status === "poor_quality") {
    badgeIcon = "⚠️";
    badgeText = isTe ? "నాణ్యత లోపం (POOR QUALITY)" : "POOR QUALITY";
    borderLeftColor = "#F59E0B";
    reasonStyle = "background-color: #FFFBEB; border: 1px solid #FDE68A; color: #92400E;";
  } else if (status === "invalid_type" || status === "invalid" || status === "needs_review" || status === "needs_attention") {
    badgeIcon = "❌";
    badgeText = isTe ? "తప్పుడు పత్రం (INVALID DOCUMENT TYPE)" : "INVALID DOCUMENT TYPE";
    borderLeftColor = "var(--danger)";
    reasonStyle = "background-color: #FEF2F2; border: 1px solid #FCA5A5; color: #991B1B;";
  } else if (status === "missing") {
    badgeIcon = "📁";
    badgeText = isTe ? "లభ్యం కాలేదు (MISSING)" : "MISSING";
    borderLeftColor = "var(--missing)";
    reasonStyle = "background-color: #F3F4F6; border: 1px solid #D1D5DB; color: #374151;";
  }

  const confidenceLabelText = (typeof t === 'function') ? t("confidence_label") : "Confidence:";
  const extractedTextLabelText = (typeof t === 'function') ? t("extracted_text_label") : "View Extracted OCR Text Snippet";
  const btnReplaceText = isTe ? "🔄 పత్రాన్ని మార్చండి" : "🔄 Replace Document";
  const detectedDoc = r.detected_document || r.detected_name;

  return `
    <div class="step-card" style="border-left: 5px solid ${borderLeftColor}; padding: 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
            <h4 style="font-size: 1.15rem; margin: 0;">
              ${escapeHtml(r.document_name)}
              ${r.is_mandatory ? `<span style="color:red; font-size: 0.8rem;">(${isTe ? 'అవసరం' : 'Mandatory'})</span>` : ''}
            </h4>
          </div>
          ${r.original_filename ? `<div style="font-size: 0.82rem; color: var(--text-muted);">${isTe ? 'ఫైల్:' : 'File:'} ${escapeHtml(r.original_filename)}</div>` : ''}
          ${detectedDoc && status !== 'missing' ? `<div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 3px;"><strong>${isTe ? 'గుర్తించబడిన పత్రం:' : 'Detected Document:'}</strong> ${escapeHtml(detectedDoc)}</div>` : ''}
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
          <span class="status-badge ${status}">
            ${badgeIcon} ${escapeHtml(badgeText)}
          </span>
          <span style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted);">
            ${escapeHtml(confidenceLabelText)} ${r.confidence || 0}%
          </span>
        </div>
      </div>

      <!-- Clear Reason Box Right Below Header -->
      <div style="margin-top: 1rem; padding: 12px 16px; border-radius: var(--border-radius-sm); font-size: 0.95rem; font-weight: 500; ${reasonStyle}">
        <strong>${badgeIcon} ${isTe ? 'వివరణ:' : 'Status:'}</strong> ${escapeHtml(r.reason || 'Document checked.')}
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.85rem; flex-wrap: wrap; gap: 8px;">
        <div>
          ${(r.extracted_text_snippet || r.extracted_text) ? `
            <details style="font-size: 0.82rem; color: var(--text-muted);">
              <summary style="cursor: pointer; font-weight: 600;">${escapeHtml(extractedTextLabelText)}</summary>
              <pre style="white-space: pre-wrap; background: #FFFFFF; border: 1px solid var(--border-color); padding: 8px; border-radius: 4px; margin-top: 4px;">${escapeHtml(r.extracted_text_snippet || r.extracted_text)}</pre>
            </details>
          ` : '<div></div>'}
        </div>
        <div>
          <button type="button" class="btn-secondary" style="font-size: 0.85rem; padding: 6px 14px; font-weight: 600;" onclick="replaceDocumentInVerification('${r.document_id}', '${escapeHtml(r.document_name)}')">
            ${escapeHtml(btnReplaceText)}
          </button>
        </div>
      </div>
    </div>
  `;
}

async function replaceDocumentInVerification(documentId, documentName) {
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get("session_id") || SessionStore.getSessionId() || SessionStore.createNewSession();
  const serviceId = urlParams.get("service_id") || sessionStorage.getItem('active_service_id') || "srv_gov_doc_verify";
  const appType = urlParams.get("app_type") || urlParams.get("application_type") || sessionStorage.getItem('active_app_type') || "new";

  // Create temporary hidden file picker
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = ".pdf,.jpg,.jpeg,.png";
  fileInput.style.display = "none";
  document.body.appendChild(fileInput);

  fileInput.onchange = async () => {
    if (!fileInput.files || fileInput.files.length === 0) {
      document.body.removeChild(fileInput);
      return;
    }

    const file = fileInput.files[0];
    document.body.removeChild(fileInput);

    const ext = file.name.split('.').pop().toLowerCase();
    const allowed = ['pdf', 'jpg', 'jpeg', 'png'];
    if (!allowed.includes(ext)) {
      alert("Unsupported file format. Please select a PDF, JPG, JPEG, or PNG file.");
      return;
    }

    if (file.size > 8 * 1024 * 1024) {
      alert(`File size (${(file.size / (1024 * 1024)).toFixed(2)} MB) exceeds maximum allowed limit of 8 MB.`);
      return;
    }

    const progressBox = document.getElementById("pipeline-progress-box");
    const resultsContainer = document.getElementById("results-container");
    if (progressBox) progressBox.style.display = "block";
    if (resultsContainer) resultsContainer.style.display = "none";

    const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
    const replacingMsg = (lang === "te") ? `నవీకరిస్తోంది: ${documentName}...` : `Replacing ${documentName} & re-verifying...`;
    updateStepUI(1, replacingMsg);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("service_id", serviceId);
    formData.append("document_id", documentId);
    formData.append("session_id", sessionId);

    try {
      const token = AuthStore.getToken();
      const headers = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const uploadResp = await fetch(`${API_BASE}/uploads`, {
        method: "POST",
        headers: headers,
        body: formData
      });

      if (!uploadResp.ok) {
        const errData = await uploadResp.json();
        if (progressBox) progressBox.style.display = "none";
        if (resultsContainer) resultsContainer.style.display = "block";
        alert(errData.error || "Replacement upload failed.");
        return;
      }

      // Re-run OCR + OpenCV + Gemini verification pipeline on updated session
      await executeVerification(sessionId, serviceId, appType);

    } catch (e) {
      if (progressBox) progressBox.style.display = "none";
      if (resultsContainer) resultsContainer.style.display = "block";
      alert("Network error replacing document.");
    }
  };

  fileInput.click();
}

function updateStepUI(stepNum, text) {
  return new Promise(resolve => {
    const textEl = document.getElementById("pipeline-status-text");
    if (textEl) textEl.textContent = text;
    resolve();
  });
}

function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function escapeHtml(str) {
  return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
}
