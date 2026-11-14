document.addEventListener("DOMContentLoaded", () => {
  checkUrlToken();
  initAuthNavbar();
  initLoginForm();
  initSignupForm();
  initRealtimePasswordValidation();
  initForgotPasswordModal();
  initPasswordToggles();
});

// Extract token from URL query string if redirected from Google OAuth
function checkUrlToken() {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get("token");
  if (token) {
    AuthStore.setToken(token);
    // Remove token parameter from URL bar for clean UI
    const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.history.replaceState({ path: cleanUrl }, "", cleanUrl);
    if (!window.location.pathname.endsWith("dashboard.html")) {
      window.location.href = "dashboard.html";
    }
    return;
  }

  const errorParam = urlParams.get("error");
  const alertBox = document.getElementById("login-alert");
  if (errorParam && alertBox) {
    const lang = (typeof getLanguage === 'function') ? getLanguage() : "en";
    let msg = "";
    if (errorParam === "unregistered_google") {
      msg = (lang === "te") ? "ఈ ఈమెయిల్ నమోదు చేయబడలేదు. దయచేసి ముందుగా సైన్ అప్ చేయండి." : "This email is not registered. Please Sign Up first.";
    } else {
      msg = decodeURIComponent(errorParam);
    }
    showAlert(alertBox, msg, "danger");
    const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.history.replaceState({ path: cleanUrl }, "", cleanUrl);
  }
}

// Update navbar based on user authentication state & current language
async function initAuthNavbar() {
  const token = AuthStore.getToken();
  const navContainer = document.getElementById("nav-auth-container");
  if (!navContainer) return;

  const myVerificationsText = (typeof t === 'function') ? t("nav_my_verifications") : "My Verifications";
  const logoutText = (typeof t === 'function') ? t("nav_logout") : "Logout";
  const signInText = (typeof t === 'function') ? t("nav_signin") : "Sign In";
  const signUpText = (typeof t === 'function') ? t("nav_signup") : "Sign Up";

  if (token) {
    try {
      const resp = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (resp.ok) {
        const data = await resp.json();
        const user = data.user;
        AuthStore.setUser(user);

        navContainer.innerHTML = `
          <div style="display: flex; align-items: center; gap: 15px;">
            <a href="profile.html" style="font-weight: 600; color: var(--primary); font-size: 0.9rem; text-decoration: none;" title="View Profile">
              👤 ${escapeHtml(user.name)}
            </a>
            <button id="btn-logout" class="btn-secondary" style="padding: 4px 12px; font-size: 0.85rem;">${escapeHtml(logoutText)}</button>
          </div>
        `;

        document.getElementById("btn-logout")?.addEventListener("click", handleLogout);
        return;
      }
    } catch (e) {
      console.warn("Session check failed", e);
    }
  }

  // Guest navbar state
  navContainer.innerHTML = `
    <a href="login.html">${escapeHtml(signInText)}</a>
    <a href="signup.html" class="btn-nav-accent">${escapeHtml(signUpText)}</a>
  `;
}

// Login Form Handler
function initLoginForm() {
  const loginForm = document.getElementById("login-form");
  if (!loginForm) return;

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertBox = document.getElementById("login-alert");
    const submitBtn = document.getElementById("login-submit-btn");

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
      const msg = (getLanguage() === "te") ? "దయచేసి ఈమెయిల్ మరియు పాస్‌వర్డ్ రెండింటినీ నమోదు చేయండి." : "Please enter both email and password.";
      showAlert(alertBox, msg, "danger");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = (getLanguage() === "te") ? "సైన్ ఇన్ అవుతోంది..." : "Signing In...";

    try {
      const resp = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      const data = await resp.json();
      if (!resp.ok) {
        showAlert(alertBox, data.error || "Login failed.", "danger");
        submitBtn.disabled = false;
        submitBtn.innerHTML = t("nav_signin");
        return;
      }

      const succMsg = (getLanguage() === "te") ? "సైన్ ఇన్ విజయం! దారి మళ్లించబడుతోంది..." : "Login successful! Redirecting...";
      showAlert(alertBox, succMsg, "success");
      AuthStore.setToken(data.token);
      AuthStore.setUser(data.user);

      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 1000);
    } catch (err) {
      showAlert(alertBox, "Network error. Please try again.", "danger");
      submitBtn.disabled = false;
      submitBtn.innerHTML = t("nav_signin");
    }
  });
}

// Signup Form Handler
function initSignupForm() {
  const signupForm = document.getElementById("signup-form");
  if (!signupForm) return;

  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertBox = document.getElementById("signup-alert");
    const submitBtn = document.getElementById("signup-submit-btn");

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm_password").value;

    if (!name || !email || !password) {
      const msg = (getLanguage() === "te") ? "దయచేసి అవసరమైన అన్ని వివరాలను నింపండి." : "Please fill in all required fields.";
      showAlert(alertBox, msg, "danger");
      return;
    }

    // Client-side strong password validation check
    const hasLength = password.length >= 8;
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[@#$%&!^&*()_+=\-\[\]{};:\'",.<>?/\\|`~]/.test(password);

    if (!hasLength || !hasUpper || !hasLower || !hasNumber || !hasSpecial) {
      const msg = (getLanguage() === "te")
        ? "మీ పాస్‌వర్డ్ తగినంత బలంగా లేదు. దయచేసి మరింత బలమైన పాస్‌వర్డ్‌ను సృష్టించండి."
        : "Your password is not strong enough. Please create a stronger password.";
      showAlert(alertBox, msg, "danger");
      const strengthContainer = document.getElementById("password-strength-container");
      if (strengthContainer) strengthContainer.style.display = "block";
      document.getElementById("password").focus();
      return;
    }

    if (password !== confirmPassword) {
      const msg = (getLanguage() === "te") ? "పాస్‌వర్డ్‌లు సరిపోలలేదు." : "Passwords do not match.";
      showAlert(alertBox, msg, "danger");
      document.getElementById("confirm_password").focus();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = (getLanguage() === "te") ? "ఖాతా సృష్టించబడుతోంది..." : "Creating Account...";

    try {
      const resp = await fetch(`${API_BASE}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          password,
          confirm_password: confirmPassword
        })
      });

      const data = await resp.json();
      if (!resp.ok) {
        showAlert(alertBox, data.error || "Signup failed.", "danger");
        submitBtn.disabled = false;
        submitBtn.innerHTML = t("btn_create_account");
        return;
      }

      const succMsg = (getLanguage() === "te") ? "ఖాతా విజయవంతంగా సృష్టించబడింది! డ్యాష్‌బోర్డ్‌కు వెళ్తోంది..." : "Account created successfully! Redirecting to Dashboard...";
      showAlert(alertBox, succMsg, "success");
      AuthStore.setToken(data.token);
      AuthStore.setUser(data.user);

      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 1000);
    } catch (err) {
      showAlert(alertBox, "Network error during signup.", "danger");
      submitBtn.disabled = false;
      submitBtn.innerHTML = t("btn_create_account");
    }
  });
}

// Real-Time Strong Password Validation Handler for Sign Up
function initRealtimePasswordValidation() {
  const passwordInput = document.getElementById("password");
  const confirmInput = document.getElementById("confirm_password");
  const strengthContainer = document.getElementById("password-strength-container");
  const strengthBar = document.getElementById("password-strength-bar");
  const strengthBadge = document.getElementById("password-strength-badge");
  const strengthMessage = document.getElementById("password-strength-message");
  const confirmMatchMsg = document.getElementById("confirm-password-match-msg");

  if (!passwordInput || !strengthContainer) return;

  const rules = {
    length: { el: document.getElementById("rule-length"), test: val => val.length >= 8 },
    uppercase: { el: document.getElementById("rule-uppercase"), test: val => /[A-Z]/.test(val) },
    lowercase: { el: document.getElementById("rule-lowercase"), test: val => /[a-z]/.test(val) },
    number: { el: document.getElementById("rule-number"), test: val => /[0-9]/.test(val) },
    special: { el: document.getElementById("rule-special"), test: val => /[@#$%&!^&*()_+=\-\[\]{};:\'",.<>?/\\|`~]/.test(val) }
  };

  const evaluatePassword = () => {
    const val = passwordInput.value;
    if (!val) {
      strengthContainer.style.display = "none";
      return { count: 0, isStrong: false };
    }

    strengthContainer.style.display = "block";
    let passedCount = 0;

    for (const [key, rule] of Object.entries(rules)) {
      if (!rule.el) continue;
      const passed = rule.test(val);
      const iconSpan = rule.el.querySelector(".criteria-icon");
      if (passed) {
        passedCount++;
        rule.el.classList.add("fulfilled");
        rule.el.classList.remove("unfulfilled");
        rule.el.style.color = "#15803D";
        if (iconSpan) {
          iconSpan.textContent = "✓";
          iconSpan.style.color = "#16A34A";
        }
      } else {
        rule.el.classList.add("unfulfilled");
        rule.el.classList.remove("fulfilled");
        rule.el.style.color = "#64748B";
        if (iconSpan) {
          iconSpan.textContent = "✗";
          iconSpan.style.color = "#DC2626";
        }
      }
    }

    const isTe = (typeof getLanguage === 'function') && getLanguage() === "te";

    if (passedCount === 5) {
      strengthBar.style.width = "100%";
      strengthBar.style.backgroundColor = "#16A34A";
      strengthBadge.textContent = isTe ? "బలమైన పాస్‌వర్డ్" : "Strong Password";
      strengthBadge.style.backgroundColor = "#DCFCE7";
      strengthBadge.style.color = "#166534";
      strengthMessage.textContent = isTe ? "బలమైన పాస్‌వర్డ్ – అన్ని భద్రతా అవసరాలు సంతృప్తికరంగా ఉన్నాయి." : "Strong Password – All security requirements are satisfied.";
      strengthMessage.style.color = "#166534";
    } else if (passedCount >= 2) {
      strengthBar.style.width = `${passedCount * 20}%`;
      strengthBar.style.backgroundColor = "#D97706";
      strengthBadge.textContent = isTe ? "మధ్యస్థ పాస్‌వర్డ్" : "Medium Password";
      strengthBadge.style.backgroundColor = "#FEF3C7";
      strengthBadge.style.color = "#B45309";
      strengthMessage.textContent = isTe ? "మధ్యస్థ పాస్‌వర్డ్ – కొన్ని అవసరాలు ఇంకా మిగిలి ఉన్నాయి." : "Medium Password – Some requirements are still missing.";
      strengthMessage.style.color = "#B45309";
    } else {
      strengthBar.style.width = `${Math.max(passedCount * 20, 15)}%`;
      strengthBar.style.backgroundColor = "#DC2626";
      strengthBadge.textContent = isTe ? "బలహీనమైన పాస్‌వర్డ్" : "Weak Password";
      strengthBadge.style.backgroundColor = "#FEE2E2";
      strengthBadge.style.color = "#DC2626";
      strengthMessage.textContent = isTe ? "బలహీనమైన పాస్‌వర్డ్ – పాస్‌వర్డ్ అవసరాలను తీర్చడం లేదు." : "Weak Password – Password does not meet the requirements.";
      strengthMessage.style.color = "#DC2626";
    }

    checkConfirmMatch();

    return { count: passedCount, isStrong: passedCount === 5 };
  };

  const checkConfirmMatch = () => {
    if (!confirmInput || !confirmMatchMsg) return;
    const p1 = passwordInput.value;
    const p2 = confirmInput.value;
    if (!p2) {
      confirmMatchMsg.style.display = "none";
      return;
    }

    confirmMatchMsg.style.display = "block";
    const isTe = (typeof getLanguage === 'function') && getLanguage() === "te";
    if (p1 === p2) {
      confirmMatchMsg.style.color = "#166534";
      confirmMatchMsg.innerHTML = isTe ? "✓ పాస్‌వర్డ్‌లు సరిపోలాయి" : "✓ Passwords match";
    } else {
      confirmMatchMsg.style.color = "#DC2626";
      confirmMatchMsg.innerHTML = isTe ? "✗ పాస్‌వర్డ్‌లు సరిపోలలేదు" : "✗ Passwords do not match";
    }
  };

  passwordInput.addEventListener("input", evaluatePassword);
  passwordInput.addEventListener("focus", () => {
    if (passwordInput.value) evaluatePassword();
  });

  if (confirmInput) {
    confirmInput.addEventListener("input", checkConfirmMatch);
  }
}



// Forgot Password & OTP Reset Modal Handler
function initForgotPasswordModal() {
  const openBtn = document.getElementById("open-forgot-modal");
  const closeBtn = document.getElementById("close-forgot-modal");
  const modal = document.getElementById("forgot-modal");
  if (!modal) return;

  const alertBox = document.getElementById("forgot-alert");
  const step1 = document.getElementById("forgot-step-1");
  const step2 = document.getElementById("forgot-step-2");
  const step3 = document.getElementById("forgot-step-3");
  const step4 = document.getElementById("forgot-step-4");

  const btnRequestOtp = document.getElementById("btn-request-otp");
  const btnVerifyOtp = document.getElementById("btn-verify-otp");
  const btnResendOtp = document.getElementById("btn-resend-otp");
  const btnSubmitReset = document.getElementById("btn-submit-reset");
  const btnForgotDone = document.getElementById("btn-forgot-done");

  let currentEmail = "";
  let currentOtp = "";
  let timerInterval = null;

  const showStep = (stepNum) => {
    step1.style.display = stepNum === 1 ? "block" : "none";
    step2.style.display = stepNum === 2 ? "block" : "none";
    step3.style.display = stepNum === 3 ? "block" : "none";
    step4.style.display = stepNum === 4 ? "block" : "none";
    alertBox.style.display = "none";
  };

  const startTimer = (durationSeconds) => {
    clearInterval(timerInterval);
    let remaining = durationSeconds;
    const timerDisplay = document.getElementById("otp-timer");

    const updateDisplay = () => {
      const mins = Math.floor(remaining / 60);
      const secs = remaining % 60;
      if (timerDisplay) {
        timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      }
      if (remaining <= 0) {
        clearInterval(timerInterval);
        if (timerDisplay) timerDisplay.textContent = "00:00 (Expired)";
      }
      remaining--;
    };
    updateDisplay();
    timerInterval = setInterval(updateDisplay, 1000);
  };

  if (openBtn) {
    openBtn.addEventListener("click", (e) => {
      e.preventDefault();
      const loginEmail = document.getElementById("email")?.value || "";
      if (loginEmail) document.getElementById("forgot-email").value = loginEmail;
      showStep(1);
      modal.style.display = "flex";
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
      clearInterval(timerInterval);
    });
  }

  // Step 1: Request OTP
  if (btnRequestOtp) {
    btnRequestOtp.addEventListener("click", async () => {
      const email = document.getElementById("forgot-email").value.trim();
      if (!email || !email.includes("@")) {
        showAlert(alertBox, "Please enter a valid email address.", "danger");
        return;
      }

      currentEmail = email;
      btnRequestOtp.disabled = true;
      btnRequestOtp.innerHTML = "Sending OTP...";

      try {
        const resp = await fetch(`${API_BASE}/auth/forgot-password`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email })
        });

        const data = await resp.json();
        btnRequestOtp.disabled = false;
        btnRequestOtp.innerHTML = t("btn_send_otp");

        if (!resp.ok) {
          showAlert(alertBox, data.error || "Failed to send OTP.", "danger");
          return;
        }

        document.getElementById("sent-otp-email").textContent = email;
        showStep(2);
        startTimer(10 * 60); // 10 minutes

        const otpInput = document.getElementById("forgot-otp");
        const otpCode = data.otp || data.dev_otp;
        if (otpInput && otpCode) {
          otpInput.value = otpCode;
        }

        let alertMsg = data.message || `Password reset OTP code has been sent to ${email}.`;
        if (otpCode) {
          alertMsg += `<div style="margin-top: 8px; font-weight: 700; color: #065F46;">🔑 Your OTP Code: <span style="font-size: 1.25rem; letter-spacing: 3px; color: #D97706; font-family: monospace; background: #FFFFFF; padding: 2px 10px; border-radius: 4px; border: 1px solid #FCD34D;">${otpCode}</span></div>`;
        }
        showAlert(alertBox, alertMsg, "success");
      } catch (err) {
        btnRequestOtp.disabled = false;
        btnRequestOtp.innerHTML = t("btn_send_otp");
        showAlert(alertBox, "Network error. Failed to request OTP.", "danger");
      }
    });
  }

  // Resend OTP
  if (btnResendOtp) {
    btnResendOtp.addEventListener("click", () => {
      showStep(1);
      clearInterval(timerInterval);
    });
  }

  // Step 2: Verify OTP Code
  if (btnVerifyOtp) {
    btnVerifyOtp.addEventListener("click", async () => {
      const otp = document.getElementById("forgot-otp").value.trim();
      if (!otp || otp.length < 6) {
        showAlert(alertBox, "Please enter the 6-digit OTP code.", "danger");
        return;
      }

      currentOtp = otp;
      btnVerifyOtp.disabled = true;
      btnVerifyOtp.innerHTML = "Verifying...";

      try {
        const resp = await fetch(`${API_BASE}/auth/verify-otp`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: currentEmail, otp })
        });

        const data = await resp.json();
        btnVerifyOtp.disabled = false;
        btnVerifyOtp.innerHTML = t("btn_verify_otp");

        if (!resp.ok) {
          showAlert(alertBox, data.error || "Invalid OTP.", "danger");
          return;
        }

        showStep(3);
        clearInterval(timerInterval);
      } catch (err) {
        btnVerifyOtp.disabled = false;
        btnVerifyOtp.innerHTML = t("btn_verify_otp");
        showAlert(alertBox, "Network error during OTP verification.", "danger");
      }
    });
  }

  // Step 3: Reset Password
  if (btnSubmitReset) {
    btnSubmitReset.addEventListener("click", async () => {
      const newPassword = document.getElementById("forgot-new-password").value;
      const confirmPassword = document.getElementById("forgot-confirm-password").value;

      if (!newPassword || newPassword.length < 6) {
        showAlert(alertBox, "Password must be at least 6 characters long.", "danger");
        return;
      }

      if (newPassword !== confirmPassword) {
        showAlert(alertBox, "New passwords do not match.", "danger");
        return;
      }

      btnSubmitReset.disabled = true;
      btnSubmitReset.innerHTML = "Resetting Password...";

      try {
        const resp = await fetch(`${API_BASE}/auth/reset-password`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: currentEmail,
            otp: currentOtp,
            new_password: newPassword,
            confirm_password: confirmPassword
          })
        });

        const data = await resp.json();
        btnSubmitReset.disabled = false;
        btnSubmitReset.innerHTML = t("btn_reset_password");

        if (!resp.ok) {
          showAlert(alertBox, data.error || "Password reset failed.", "danger");
          return;
        }

        showStep(4);
      } catch (err) {
        btnSubmitReset.disabled = false;
        btnSubmitReset.innerHTML = t("btn_reset_password");
        showAlert(alertBox, "Network error during password reset.", "danger");
      }
    });
  }

  // Step 4: Done
  if (btnForgotDone) {
    btnForgotDone.addEventListener("click", () => {
      modal.style.display = "none";
      if (document.getElementById("email")) {
        document.getElementById("email").value = currentEmail;
      }
    });
  }
}

// Logout Handler
async function handleLogout() {
  const token = AuthStore.getToken();
  try {
    await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }
    });
  } catch (e) {}

  AuthStore.clearToken();
  AuthStore.clearUser();
  window.location.href = "index.html";
}

function showAlert(el, msg, type) {
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.innerHTML = msg;
  el.style.display = "block";
}

function escapeHtml(str) {
  return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
}

const LUCIDE_EYE_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide-icon lucide-eye"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>`;
const LUCIDE_EYE_OFF_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide-icon lucide-eye-off"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/></svg>`;

// Password Field Visibility Toggle Handlers with Lucide outline icons
function togglePasswordVisibility(inputId, btn) {
  const input = typeof inputId === "string" ? document.getElementById(inputId) : inputId;
  if (!input) return;

  if (input.type === "password") {
    input.type = "text";
    if (btn) {
      btn.innerHTML = LUCIDE_EYE_ICON;
      btn.setAttribute("title", "Hide password");
      btn.setAttribute("aria-label", "Hide password");
    }
  } else {
    input.type = "password";
    if (btn) {
      btn.innerHTML = LUCIDE_EYE_OFF_ICON;
      btn.setAttribute("title", "Show password");
      btn.setAttribute("aria-label", "Show password");
    }
  }
}

function initPasswordToggles() {
  const passwordInputs = document.querySelectorAll('input[type="password"]');
  passwordInputs.forEach(input => {
    if (input.dataset.hasToggle === "true") return;

    // Ensure parent element has position relative & password-wrapper class
    let wrapper = input.parentElement;
    if (!wrapper || !wrapper.classList.contains("password-wrapper")) {
      wrapper = document.createElement("div");
      wrapper.className = "password-wrapper";
      wrapper.style.position = "relative";
      wrapper.style.width = "100%";
      input.parentNode.insertBefore(wrapper, input);
      wrapper.appendChild(input);
    }

    input.style.paddingRight = "44px";

    // Check if toggle button already exists inside wrapper
    let toggleBtn = wrapper.querySelector(".password-toggle-btn");
    if (!toggleBtn) {
      toggleBtn = document.createElement("button");
      toggleBtn.type = "button";
      toggleBtn.className = "password-toggle-btn";
      toggleBtn.innerHTML = LUCIDE_EYE_OFF_ICON;
      toggleBtn.title = "Show password";
      toggleBtn.setAttribute("aria-label", "Show password");
      toggleBtn.addEventListener("click", (e) => {
        e.preventDefault();
        togglePasswordVisibility(input, toggleBtn);
      });
      wrapper.appendChild(toggleBtn);
    }

    input.dataset.hasToggle = "true";
  });
}

