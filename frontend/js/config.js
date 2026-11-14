// REST API Base URL
const API_BASE = '/api';

// Local storage session helpers
const AuthStore = {
  getToken: () => localStorage.getItem('gov_auth_token') || sessionStorage.getItem('gov_auth_token'),
  setToken: (token) => {
    localStorage.setItem('gov_auth_token', token);
    sessionStorage.setItem('gov_auth_token', token);
  },
  clearToken: () => {
    localStorage.removeItem('gov_auth_token');
    sessionStorage.removeItem('gov_auth_token');
  },
  getUser: () => {
    const raw = localStorage.getItem('gov_user_profile');
    return raw ? JSON.parse(raw) : null;
  },
  setUser: (user) => {
    localStorage.setItem('gov_user_profile', JSON.stringify(user));
  },
  clearUser: () => {
    localStorage.removeItem('gov_user_profile');
  }
};

// Unique verification session generator helper
const SessionStore = {
  getSessionId: () => {
    let sid = sessionStorage.getItem('current_verification_session');
    if (!sid) {
      sid = 'session_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now();
      sessionStorage.setItem('current_verification_session', sid);
    }
    return sid;
  },
  createNewSession: () => {
    const sid = 'session_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now();
    sessionStorage.setItem('current_verification_session', sid);
    return sid;
  },
  resetSession: () => {
    sessionStorage.removeItem('current_verification_session');
  }
};
