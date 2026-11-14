document.addEventListener("DOMContentLoaded", () => {
  loadUserProfile();
});

async function loadUserProfile() {
  const container = document.getElementById("profile-container");
  if (!container) return;

  const token = AuthStore.getToken();
  if (!token) {
    container.innerHTML = `
      <div class="alert alert-warning">
        Please <a href="login.html">Sign In</a> to view and edit your profile settings.
      </div>
    `;
    return;
  }

  try {
    const resp = await fetch(`${API_BASE}/auth/profile`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const data = await resp.json();

    if (!resp.ok) {
      container.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error || 'Failed to load profile.')}</div>`;
      return;
    }

    const p = data.profile;
    renderProfileView(container, p);

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Error retrieving user profile.</div>`;
  }
}

function renderProfileView(container, profile) {
  const stats = profile.stats || {};

  container.innerHTML = `
    <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; align-items: start;">
      
      <!-- Left Column: User Card & Stats -->
      <div>
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--border-radius-lg); padding: 2rem; text-align: center; box-shadow: var(--shadow-sm); margin-bottom: 1.5rem;">
          <div style="width: 80px; height: 80px; background: var(--primary); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.2rem; margin: 0 auto 1rem; font-weight: 700;">
            ${escapeHtml(profile.name.charAt(0).toUpperCase())}
          </div>
          <h3 style="margin: 0 0 4px 0; font-size: 1.3rem;" id="profile-display-name">${escapeHtml(profile.name)}</h3>
          <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;">${escapeHtml(profile.email)}</p>
          <span class="hero-badge" style="background: var(--bg-primary); border: 1px solid var(--border-color); font-size: 0.78rem;">
            🔐 ${escapeHtml(profile.auth_provider)}
          </span>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 1rem;">
            Member since: <strong>${escapeHtml(profile.member_since)}</strong>
          </div>
        </div>

        <!-- Verification Stats Tile -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--border-radius-lg); padding: 1.5rem; box-shadow: var(--shadow-sm);">
          <h4 style="margin-top: 0; margin-bottom: 1rem; font-size: 1rem;">📊 Verification Activity</h4>
          <div style="display: flex; flex-direction: column; gap: 0.75rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
              <span style="color: var(--text-muted);">Total Sessions:</span>
              <strong>${stats.total_verifications || 0}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
              <span style="color: var(--success);">Ready Status:</span>
              <strong style="color: var(--success);">${stats.ready_verifications || 0}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
              <span style="color: var(--warning);">Needs Attention:</span>
              <strong style="color: var(--warning);">${stats.pending_verifications || 0}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Edit Profile & Password Forms -->
      <div style="display: flex; flex-direction: column; gap: 2rem;">
        
        <!-- Form 1: Edit Profile Info -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--border-radius-lg); padding: 2rem; box-shadow: var(--shadow-sm);">
          <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.2rem;">👤 Personal Information</h3>
          <p style="color: var(--text-muted); font-size: 0.88rem; margin-bottom: 1.5rem;">Update your registered account name.</p>
          
          <div id="profile-update-alert" style="display: none; margin-bottom: 1rem;"></div>

          <form id="edit-profile-form">
            <div class="form-group">
              <label class="form-label" for="edit-name">Full Name</label>
              <input type="text" id="edit-name" class="form-input" value="${escapeHtml(profile.name || '')}" placeholder="Your full name" required>
            </div>

            <div class="form-group">
              <label class="form-label" for="edit-email">Email Address</label>
              <input type="email" id="edit-email" class="form-input" value="${escapeHtml(profile.email || '')}" disabled style="background: var(--bg-primary); cursor: not-allowed; opacity: 0.75;">
              <p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">Email address cannot be changed for security reasons.</p>
            </div>

            <button type="submit" class="btn-primary" id="btn-save-profile">
              Save Profile Changes →
            </button>
          </form>
        </div>

        <!-- Form 2: Change Password (If Email Account) -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--border-radius-lg); padding: 2rem; box-shadow: var(--shadow-sm);">
          <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.2rem;">🔑 Security & Password</h3>
          
          ${profile.is_google_account ? `
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1rem; font-size: 0.88rem; color: var(--text-muted);">
              ℹ️ Your account is authenticated securely via <strong>Google OAuth</strong>. Password changes are managed through your Google Account.
            </div>
          ` : `
            <p style="color: var(--text-muted); font-size: 0.88rem; margin-bottom: 1.5rem;">Update your account password using your current password.</p>
            
            <div id="password-change-alert" style="display: none; margin-bottom: 1rem;"></div>

            <form id="change-password-form">
              <div class="form-group">
                <label class="form-label" for="current-password">Current Password</label>
                <div class="password-wrapper">
                  <input type="password" id="current-password" class="form-input password-input-styled" placeholder="••••••••" style="background-color: #F0F9FF; border: 1px solid #BAE6FD;" required>
                  <button type="button" class="password-toggle-btn" title="Show password" aria-label="Show password" onclick="togglePasswordVisibility('current-password', this)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide-icon lucide-eye-off"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/></svg>
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label" for="new-password">New Password</label>
                <div class="password-wrapper">
                  <input type="password" id="new-password" class="form-input password-input-styled" placeholder="At least 8 characters" minlength="8" style="background-color: #F0F9FF; border: 1px solid #BAE6FD;" required>
                  <button type="button" class="password-toggle-btn" title="Show password" aria-label="Show password" onclick="togglePasswordVisibility('new-password', this)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide-icon lucide-eye-off"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/></svg>
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label" for="confirm-new-password">Confirm New Password</label>
                <div class="password-wrapper">
                  <input type="password" id="confirm-new-password" class="form-input password-input-styled" placeholder="Repeat new password" style="background-color: #F0F9FF; border: 1px solid #BAE6FD;" required>
                  <button type="button" class="password-toggle-btn" title="Show password" aria-label="Show password" onclick="togglePasswordVisibility('confirm-new-password', this)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide-icon lucide-eye-off"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/></svg>
                  </button>
                </div>
              </div>

              <button type="submit" class="btn-primary" id="btn-change-password">
                Update Password →
              </button>
            </form>
          `}
        </div>

      </div>

    </div>
  `;

  // Attach event listeners for forms
  initProfileFormListeners(profile);
}

function initProfileFormListeners(profile) {
  const token = AuthStore.getToken();

  // Edit Profile Form Submit
  const editForm = document.getElementById("edit-profile-form");
  if (editForm) {
    editForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const alertBox = document.getElementById("profile-update-alert");
      const submitBtn = document.getElementById("btn-save-profile");
      const newName = document.getElementById("edit-name").value.trim();
      if (!newName) return;

      submitBtn.disabled = true;
      submitBtn.textContent = "Saving...";

      try {
        const resp = await fetch(`${API_BASE}/auth/profile`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({ name: newName })
        });

        const data = await resp.json();
        submitBtn.disabled = false;
        submitBtn.textContent = "Save Profile Changes →";

        if (!resp.ok) {
          showProfileAlert(alertBox, data.error || "Failed to update profile.", "danger");
          return;
        }

        showProfileAlert(alertBox, "Profile updated successfully!", "success");
        document.getElementById("profile-display-name").textContent = newName;
        
        // Update local store
        const u = AuthStore.getUser() || {};
        u.name = newName;
        AuthStore.setUser(u);

        // Re-initialize navbar to reflect new name
        if (typeof initAuthNavbar === 'function') initAuthNavbar();

      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Save Profile Changes →";
        showProfileAlert(alertBox, "Network error updating profile.", "danger");
      }
    });
  }

  // Change Password Form Submit
  const passwordForm = document.getElementById("change-password-form");
  if (passwordForm) {
    passwordForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const alertBox = document.getElementById("password-change-alert");
      const submitBtn = document.getElementById("btn-change-password");

      const currentPassword = document.getElementById("current-password").value;
      const newPassword = document.getElementById("new-password").value;
      const confirmNewPassword = document.getElementById("confirm-new-password").value;

      if (newPassword.length < 6) {
        showProfileAlert(alertBox, "New password must be at least 6 characters.", "danger");
        return;
      }

      if (newPassword !== confirmNewPassword) {
        showProfileAlert(alertBox, "New password and Confirm Password do not match.", "danger");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Updating...";

      try {
        const resp = await fetch(`${API_BASE}/auth/change-password`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
            confirm_password: confirmNewPassword
          })
        });

        const data = await resp.json();
        submitBtn.disabled = false;
        submitBtn.textContent = "Update Password →";

        if (!resp.ok) {
          showProfileAlert(alertBox, data.error || "Password change failed.", "danger");
          return;
        }

        showProfileAlert(alertBox, "Password updated successfully!", "success");
        passwordForm.reset();

      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Update Password →";
        showProfileAlert(alertBox, "Network error changing password.", "danger");
      }
    });
  }
}

function showProfileAlert(el, msg, type) {
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.innerHTML = msg;
  el.style.display = "block";
}

function escapeHtml(str) {
  return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
}
