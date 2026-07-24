/**
 * Admin Panel Controller Module
 * Handles Supabase/JWT authentication, leads dashboard, feature flag toggles, and content CRUD.
 */

let authToken = sessionStorage.getItem('admin_jwt_token') || null;

document.addEventListener('DOMContentLoaded', () => {
  if (authToken) {
    showDashboard();
  } else {
    showLogin();
  }

  bindAuthEvents();
  bindNavigationTabs();
  bindFeatureToggles();
  bindCrudForms();
});

/* --- Authentication --- */
function bindAuthEvents() {
  const loginForm = document.getElementById('admin-login-form');
  const logoutBtn = document.getElementById('admin-logout-btn');
  const errorMsg = document.getElementById('login-error-msg');

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (errorMsg) errorMsg.style.display = 'none';

      const email = document.getElementById('admin-email').value.trim();
      const password = document.getElementById('admin-password').value.trim();

      try {
        const res = await fetch(`${CONFIG.API_BASE_URL}/admin/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok && data.access_token) {
          authToken = data.access_token;
          sessionStorage.setItem('admin_jwt_token', authToken);
          sessionStorage.setItem('admin_email', data.email || email);
          showDashboard();
        } else {
          if (errorMsg) {
            errorMsg.textContent = data.error || 'Authentication failed.';
            errorMsg.style.display = 'block';
          }
        }
      } catch (err) {
        if (errorMsg) {
          errorMsg.textContent = 'Server connection error. Please verify backend API.';
          errorMsg.style.display = 'block';
        }
      }
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      authToken = null;
      sessionStorage.removeItem('admin_jwt_token');
      sessionStorage.removeItem('admin_email');
      showLogin();
    });
  }
}

function showLogin() {
  document.getElementById('admin-login-overlay').style.display = 'flex';
  document.getElementById('admin-dashboard-layout').style.display = 'none';
}

function showDashboard() {
  document.getElementById('admin-login-overlay').style.display = 'none';
  document.getElementById('admin-dashboard-layout').style.display = 'flex';

  const emailDisplay = document.getElementById('user-email-display');
  if (emailDisplay) {
    emailDisplay.textContent = sessionStorage.getItem('admin_email') || 'Admin User';
  }

  // Load initial tab content
  loadLeads();
  loadAdminFeatures();
}

/* --- Helper for Authorized Fetch Requests --- */
async function authFetch(url, options = {}) {
  options.headers = options.headers || {};
  options.headers['Authorization'] = `Bearer ${authToken}`;

  const res = await fetch(url, options);
  if (res.status === 401) {
    // Session expired or invalid
    authToken = null;
    sessionStorage.removeItem('admin_jwt_token');
    showLogin();
    throw new Error('Session expired. Please log in again.');
  }
  return res;
}

/* --- Tab Navigation --- */
function bindNavigationTabs() {
  const buttons = document.querySelectorAll('.admin-menu button');
  const tabs = document.querySelectorAll('.admin-tab-content');

  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      tabs.forEach(t => t.style.display = 'none');

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetTab = document.getElementById(targetId);
      if (targetTab) targetTab.style.display = 'block';

      // Load dynamic tab content when selected
      if (targetId === 'tab-leads') loadLeads();
      if (targetId === 'tab-features') loadAdminFeatures();
      if (targetId === 'tab-portfolio') loadAdminPortfolio();
      if (targetId === 'tab-profile') loadAdminProfile();
    });
  });
}

/* --- Leads Dashboard --- */
async function loadLeads() {
  const filter = document.getElementById('lead-status-filter').value;
  const tbody = document.getElementById('leads-table-body');
  if (!tbody) return;

  try {
    const url = filter ? `${CONFIG.API_BASE_URL}/admin/leads?status=${filter}` : `${CONFIG.API_BASE_URL}/admin/leads`;
    const res = await authFetch(url);
    const leads = await res.json();

    if (leads.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No inquiries found.</td></tr>`;
      return;
    }

    tbody.innerHTML = leads.map(l => `
      <tr>
        <td style="font-size: 0.85rem;">${new Date(l.created_at).toLocaleDateString()}</td>
        <td><strong>${l.name}</strong></td>
        <td style="font-size: 0.85rem;">${l.email}<br><span style="color: var(--text-muted);">${l.phone || ''}</span></td>
        <td style="font-size: 0.85rem;">${l.service_interest}</td>
        <td>
          <span class="status-badge status-${l.status}">${l.status}</span>
        </td>
        <td>
          <select class="form-select status-select" data-id="${l.id}" style="padding: 0.3rem; font-size: 0.8rem;">
            <option value="new" ${l.status === 'new' ? 'selected' : ''}>New</option>
            <option value="contacted" ${l.status === 'contacted' ? 'selected' : ''}>Contacted</option>
            <option value="closed" ${l.status === 'closed' ? 'selected' : ''}>Closed</option>
          </select>
        </td>
      </tr>
      <tr>
        <td colspan="6" style="background: rgba(255,255,255,0.02); font-size: 0.85rem; padding: 0.75rem 1rem; border-bottom: 2px solid var(--border-glass);">
          <strong>Message:</strong> "${l.message}"
        </td>
      </tr>
    `).join('');

    // Bind status update listeners
    tbody.querySelectorAll('.status-select').forEach(select => {
      select.addEventListener('change', async (e) => {
        const leadId = e.target.getAttribute('data-id');
        const newStatus = e.target.value;
        await updateLeadStatus(leadId, newStatus);
      });
    });

  } catch (err) {
    console.error('Error loading leads:', err);
  }
}

async function updateLeadStatus(leadId, status) {
  try {
    const res = await authFetch(`${CONFIG.API_BASE_URL}/admin/leads/${leadId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (res.ok) {
      loadLeads();
    }
  } catch (err) {
    alert('Failed to update lead status.');
  }
}

document.getElementById('lead-status-filter')?.addEventListener('change', loadLeads);

/* --- Feature Toggles --- */
async function loadAdminFeatures() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/features`);
    const flags = await res.json();

    Object.entries(flags).forEach(([key, value]) => {
      const toggle = document.getElementById(`toggle-${key}`);
      if (toggle) toggle.checked = value;
    });
  } catch (err) {
    console.error('Error loading admin features:', err);
  }
}

function bindFeatureToggles() {
  const switches = document.querySelectorAll('.switch input');
  switches.forEach(sw => {
    sw.addEventListener('change', async (e) => {
      const featureName = e.target.getAttribute('data-feature');
      const isEnabled = e.target.checked;

      try {
        await authFetch(`${CONFIG.API_BASE_URL}/admin/features/${featureName}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_enabled: isEnabled })
        });
      } catch (err) {
        alert('Failed to update feature toggle.');
        e.target.checked = !isEnabled; // Revert
      }
    });
  });
}

/* --- CRUD Forms --- */
function bindCrudForms() {
  // Portfolio Form
  const portForm = document.getElementById('portfolio-form');
  if (portForm) {
    portForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        title: document.getElementById('port-title').value.trim(),
        description: document.getElementById('port-desc').value.trim(),
        tech_pills: document.getElementById('port-pills').value.trim(),
        external_link: document.getElementById('port-link').value.trim(),
        youtube_video_url: document.getElementById('port-youtube').value.trim()
      };

      try {
        const res = await authFetch(`${CONFIG.API_BASE_URL}/admin/portfolio`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          portForm.reset();
          loadAdminPortfolio();
        }
      } catch (err) {
        alert('Failed to create portfolio project.');
      }
    });
  }

  // Blog Form
  const blogForm = document.getElementById('blog-form');
  if (blogForm) {
    blogForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        title: document.getElementById('blog-title').value.trim(),
        excerpt: document.getElementById('blog-excerpt').value.trim(),
        full_content: document.getElementById('blog-full-content').value.trim(),
        linkedin_url: document.getElementById('blog-linkedin').value.trim()
      };

      try {
        const res = await authFetch(`${CONFIG.API_BASE_URL}/admin/blog`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          blogForm.reset();
          alert('Blog post published successfully!');
        }
      } catch (err) {
        alert('Failed to publish blog post.');
      }
    });
  }

  // Profile Form
  const profileForm = document.getElementById('profile-form');
  if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        profile_photo_url: document.getElementById('prof-photo-url').value.trim(),
        intro_video_url: document.getElementById('prof-video-url').value.trim(),
        bio_headline: document.getElementById('prof-headline').value.trim(),
        bio_summary: document.getElementById('prof-summary').value.trim()
      };

      try {
        const res = await authFetch(`${CONFIG.API_BASE_URL}/admin/profile`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          alert('Profile settings updated successfully!');
        }
      } catch (err) {
        alert('Failed to update profile settings.');
      }
    });
  }
}

async function loadAdminPortfolio() {
  const container = document.getElementById('portfolio-list');
  if (!container) return;

  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/portfolio`);
    const projects = await res.json();

    if (projects.length === 0) {
      container.innerHTML = '<p style="color: var(--text-muted);">No portfolio projects added yet.</p>';
      return;
    }

    container.innerHTML = projects.map(p => `
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 1rem; border-bottom: 1px solid var(--border-glass);">
        <div>
          <h4>${p.title}</h4>
          <p style="font-size: 0.85rem;">${p.description.substring(0, 80)}...</p>
        </div>
        <button class="btn btn-secondary delete-port-btn" data-id="${p.id}" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;">
          Delete 🗑️
        </button>
      </div>
    `).join('');

    container.querySelectorAll('.delete-port-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = e.currentTarget.getAttribute('data-id');
        if (confirm('Delete this portfolio project?')) {
          await authFetch(`${CONFIG.API_BASE_URL}/admin/portfolio/${id}`, { method: 'DELETE' });
          loadAdminPortfolio();
        }
      });
    });

  } catch (err) {
    console.error('Error loading admin portfolio:', err);
  }
}

async function loadAdminProfile() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/profile`);
    const p = await res.json();

    if (document.getElementById('prof-photo-url')) document.getElementById('prof-photo-url').value = p.profile_photo_url || '';
    if (document.getElementById('prof-video-url')) document.getElementById('prof-video-url').value = p.intro_video_url || '';
    if (document.getElementById('prof-headline')) document.getElementById('prof-headline').value = p.bio_headline || '';
    if (document.getElementById('prof-summary')) document.getElementById('prof-summary').value = p.bio_summary || '';
  } catch (err) {
    console.error('Error loading admin profile:', err);
  }
}
