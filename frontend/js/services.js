document.addEventListener("DOMContentLoaded", () => {
  loadGovernmentServices();
});

async function loadGovernmentServices() {
  const container = document.getElementById("services-grid-container");
  if (!container) return;

  const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
  const loadingText = (lang === "te") ? "డేటాబేస్ నుండి ప్రభుత్వ సేవలను సేకరిస్తోంది..." : "Loading Government Document Verification service...";

  container.innerHTML = `
    <div style="text-align: center; padding: 3rem;">
      <div style="font-size: 1.2rem; color: var(--text-muted);">${loadingText}</div>
    </div>
  `;

  try {
    const resp = await fetch(`${API_BASE}/services`);
    let services = [];
    if (resp.ok) {
      const data = await resp.json();
      services = data.services || [];
    }

    // Identify the main Government Document Verification service
    let mainService = services.find(srv =>
      srv.id === "srv_gov_doc_verify" ||
      srv.slug === "government-document-verification" ||
      (srv.name && srv.name.toLowerCase().includes("government document"))
    );

    // Fallback definition if not found
    if (!mainService) {
      mainService = {
        id: "srv_gov_doc_verify",
        slug: "government-document-verification",
        name: "Government Document Verification",
        name_te: "ప్రభుత్వ పత్రాల పరిశీలన",
        department: "Public Document Verification Authority",
        department_te: "ప్రభుత్వ పత్రాల పరిశీలన సంస్థ",
        description: "Upload and verify various government-related documents through a single AI-powered document verification system.",
        description_te: "ఏకీకృత AI ఆధారిత పత్రాల పరిశీలన వ్యవస్థ ద్వారా వివిధ ప్రభుత్వ సంబంధిత పత్రాలను అప్‌లోడ్ చేసి పరిశీలించండి."
      };
    }

    const isTe = (lang === "te");
    const name = isTe ? (mainService.name_te || mainService.name) : mainService.name;
    const dept = isTe ? (mainService.department_te || mainService.department) : mainService.department;
    const desc = isTe ? (mainService.description_te || mainService.description) : mainService.description;
    const btnText = (typeof t === 'function' && t("btn_start_doc_verification")) ? t("btn_start_doc_verification") : "Start Document Verification →";

    container.innerHTML = `
      <div class="common-service-card">
        <div class="common-service-header">
          <div>
            <span class="common-service-badge">🏛️ ${escapeHtml(dept || 'Public Document Verification Authority')}</span>
            <h2 class="common-service-title">${escapeHtml(name)}</h2>
          </div>
        </div>

        <p class="common-service-desc">${escapeHtml(desc)}</p>

        <div style="margin-top: 1rem; display: flex; align-items: center; justify-content: flex-start;">
          <a href="documents.html?service=${encodeURIComponent(mainService.slug)}" class="btn-primary" style="font-size: 1.05rem; padding: 0.9rem 2.2rem; justify-content: center; box-shadow: 0 4px 12px rgba(217, 119, 6, 0.25);">
            ${escapeHtml(btnText)}
          </a>
        </div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Connection error. Is the Python Flask backend running?</div>`;
  }
}

function escapeHtml(str) {
  return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
}
