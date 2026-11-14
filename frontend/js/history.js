document.addEventListener("DOMContentLoaded", () => {
  loadVerificationHistory();
});

async function loadVerificationHistory() {
  const container = document.getElementById("history-container");
  if (!container) return;

  const token = AuthStore.getToken();
  if (!token) {
    container.innerHTML = `
      <div class="alert alert-warning">
        Please <a href="login.html">${typeof t === 'function' ? t('nav_signin') : 'Sign In'}</a> to view your previous document verification history.
      </div>
    `;
    return;
  }

  container.innerHTML = `<div style="text-align: center; padding: 2rem;">Loading verification history...</div>`;

  try {
    const resp = await fetch(`${API_BASE}/verification/my-verifications`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const data = await resp.json();

    if (!resp.ok) {
      container.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error || 'Failed to fetch history.')}</div>`;
      return;
    }

    const verifications = data.verifications || [];

    if (verifications.length === 0) {
      container.innerHTML = `
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 3rem; text-align: center; border-radius: var(--border-radius-lg);">
          <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📂</div>
          <h3>${typeof t === 'function' ? t('no_history_title') : 'No Verification History Yet'}</h3>
          <p style="color: var(--text-muted); margin-bottom: 1.5rem;">${typeof t === 'function' ? t('no_history_sub') : 'Perform a document readiness check to save verification records here.'}</p>
          <a href="services.html" class="btn-primary">${typeof t === 'function' ? t('btn_select_service') : 'Browse Services'}</a>
        </div>
      `;
      return;
    }

    const lang = (typeof getLanguage === 'function') ? getLanguage() : 'en';

    container.innerHTML = verifications.map(v => {
      const isReady = v.overall_status === 'READY';
      const badgeClass = isReady ? 'ready' : 'needs_attention';
      const statusLabel = isReady ? (lang === 'te' ? 'సిద్ధంగా ఉంది' : 'READY') : (lang === 'te' ? 'శ్రద్ధ వహించండి' : 'NEEDS ATTENTION');
      const serviceName = (lang === 'te' && v.service_name_te) ? v.service_name_te : v.service_name;

      const docsHtml = (v.documents && v.documents.length > 0) ? `
        <div style="margin-top: 1rem; border-top: 1px dashed var(--border-color); padding-top: 0.75rem;">
          <h5 style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 0.5rem;">
            ${lang === 'te' ? 'అప్‌లోడ్ చేసిన పత్రాలు & ఫలితాలు:' : 'Uploaded Documents & Analysis:'}
          </h5>
          <div style="display: grid; gap: 0.5rem;">
            ${v.documents.map(d => {
              let docStatusBadge = '<span class="status-badge ready">READY</span>';
              if (d.status === 'invalid') docStatusBadge = '<span class="status-badge invalid">INVALID</span>';
              else if (d.status === 'needs_attention') docStatusBadge = '<span class="status-badge needs_attention">NEEDS ATTENTION</span>';
              else if (d.status === 'missing') docStatusBadge = '<span class="status-badge missing">MISSING</span>';

              const docName = d.document_name || 'Document';
              const origFile = d.original_filename ? `(${escapeHtml(d.original_filename)})` : '';
              const detected = d.detected_document ? ` • Detected: <strong>${escapeHtml(d.detected_document)}</strong>` : '';
              const reasonMsg = d.reason ? `<div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 2px;">⚠ ${escapeHtml(d.reason)}</div>` : '';

              return `
                <div style="background: rgba(0,0,0,0.02); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.6rem 0.8rem;">
                  <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
                    <div>
                      <strong>${escapeHtml(docName)}</strong> <span style="font-size: 0.82rem; color: var(--text-muted);">${origFile}</span>
                      <span style="font-size: 0.82rem; color: var(--text-main); margin-left: 6px;">${detected}</span>
                    </div>
                    <div>${docStatusBadge}</div>
                  </div>
                  ${reasonMsg}
                </div>
              `;
            }).join('')}
          </div>
        </div>
      ` : '';

      return `
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--border-radius-lg); padding: 1.25rem 1.5rem; margin-bottom: 1.25rem; box-shadow: var(--shadow-sm);">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
            <div>
              <span style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(v.date)}</span>
              <h3 style="font-size: 1.25rem; margin: 0.2rem 0 0.5rem 0;">${escapeHtml(serviceName)}</h3>
              <div style="font-size: 0.9rem; color: var(--text-muted);">
                ${v.ready_count} / ${v.total_required} ${lang === 'te' ? 'పత్రాలు సిద్ధంగా ఉన్నాయి' : 'Documents Ready'}
              </div>
            </div>

            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem;">
              <span class="status-badge ${badgeClass}">${escapeHtml(statusLabel)}</span>
              <a href="report.html?session_id=${v.session_id}&view_only=true" class="btn-secondary" style="padding: 6px 14px; font-size: 0.85rem; text-decoration: none;">
                ${lang === 'te' ? 'పూర్తి నివేదిక చూడండి' : 'View Verification Report'}
              </a>
            </div>
          </div>

          ${docsHtml}
        </div>
      `;
    }).join('');

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Error retrieving verification history.</div>`;
  }
}

function escapeHtml(str) {
  return str ? String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
}
