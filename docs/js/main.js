/**
 * Main Application Module
 * Public frontend controller managing theme toggles, dynamic content loading,
 * blog modals, feature flag section visibility, and contact form submissions.
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initMobileMenu();
  loadSiteData();
  bindContactForm();
  bindBlogModal();
});

/* --- Theme Management --- */
function initTheme() {
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const savedTheme = localStorage.getItem('theme-preference') || 'dark';

  setTheme(savedTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      setTheme(newTheme);
      localStorage.setItem('theme-preference', newTheme);
    });
  }
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const themeIcon = document.getElementById('theme-icon');
  if (themeIcon) {
    themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
  }
}

/* --- Mobile Menu --- */
function initMobileMenu() {
  const menuBtn = document.getElementById('mobile-menu-btn');
  const navLinks = document.getElementById('nav-links');

  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('mobile-active');
    });

    // Close menu when link clicked
    navLinks.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('mobile-active');
      });
    });
  }
}

/* --- Dynamic Data Loading & Feature Flags --- */
async function loadSiteData() {
  try {
    // 1. Fetch feature flags first
    const featRes = await fetch(`${CONFIG.API_BASE_URL}/features`);
    const flags = await featRes.json();
    applyFeatureFlags(flags);

    // 2. Fetch Profile Info
    fetchProfile();

    // 3. Fetch Slideshow Images
    fetchSlideshow();

    // 4. Fetch Portfolio Projects if enabled
    if (flags.portfolio !== false) fetchPortfolio();

    // 5. Fetch Case Studies if enabled
    if (flags.case_studies !== false) fetchCaseStudies();

    // 6. Fetch Testimonials if enabled
    if (flags.testimonials !== false) fetchTestimonials();

    // 7. Fetch Blog Posts if enabled
    if (flags.blog !== false) fetchBlogPosts();

  } catch (err) {
    console.warn('Could not connect to API server. Utilizing fallback static content:', err);
  }
}

function applyFeatureFlags(flags) {
  const sectionMap = {
    services: 'services-section',
    portfolio: 'portfolio-section',
    case_studies: 'case-studies-section',
    testimonials: 'testimonials-section',
    blog: 'blog-section'
  };

  Object.entries(sectionMap).forEach(([flagName, elementId]) => {
    const sectionEl = document.getElementById(elementId);
    const navLinkEl = document.querySelector(`.nav-links a[href="#${elementId}"]`);

    if (sectionEl) {
      if (flags[flagName] === false) {
        sectionEl.style.display = 'none';
        if (navLinkEl) navLinkEl.style.display = 'none';
      } else {
        sectionEl.style.display = 'block';
        if (navLinkEl) navLinkEl.style.display = 'inline-block';
      }
    }
  });
}

async function fetchProfile() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/profile`);
    if (!res.ok) return;
    const profile = await res.json();

    const photoEl = document.getElementById('profile-photo');
    const headlineEl = document.getElementById('bio-headline');
    const summaryEl = document.getElementById('bio-summary');
    const videoIframe = document.getElementById('intro-video-iframe');

    if (photoEl && profile.profile_photo_url) photoEl.src = profile.profile_photo_url;
    if (headlineEl && profile.bio_headline) headlineEl.textContent = profile.bio_headline;
    if (summaryEl && profile.bio_summary) summaryEl.textContent = profile.bio_summary;
    if (videoIframe && profile.intro_video_url) {
      videoIframe.src = sanitizeYouTubeEmbedUrl(profile.intro_video_url);
    }
  } catch (e) {
    console.error('Error fetching profile:', e);
  }
}

async function fetchSlideshow() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/slideshow`);
    if (!res.ok) return;
    const slides = await res.json();

    if (slides && slides.length > 0) {
      new SlideshowCarousel('slideshow-container', slides);
    }
  } catch (e) {
    console.error('Error fetching slideshow:', e);
  }
}

async function fetchPortfolio() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/portfolio`);
    if (!res.ok) return;
    const projects = await res.json();
    const grid = document.getElementById('portfolio-grid');

    if (grid && projects.length > 0) {
      grid.innerHTML = projects.map(p => `
        <div class="glass-panel portfolio-card">
          <div>
            <h3>${p.title}</h3>
            <p>${p.description}</p>
            <div class="tech-pills">
              ${(p.tech_pills || []).map(pill => `<span class="tech-pill">${pill}</span>`).join('')}
            </div>
            ${p.youtube_video_url ? `
              <div class="video-container">
                <iframe src="${sanitizeYouTubeEmbedUrl(p.youtube_video_url)}" title="${p.title} Demo" loading="lazy" allowfullscreen></iframe>
              </div>
            ` : ''}
          </div>
          <div class="portfolio-links">
            ${p.external_link ? `
              <a href="${p.external_link}" target="_blank" rel="noopener" class="btn btn-secondary btn-sm">
                View Project ↗
              </a>
            ` : ''}
          </div>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error('Error fetching portfolio:', e);
  }
}

async function fetchCaseStudies() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/case-studies`);
    if (!res.ok) return;
    const studies = await res.json();
    const grid = document.getElementById('case-studies-grid');

    if (grid && studies.length > 0) {
      grid.innerHTML = studies.map(s => `
        <div class="glass-panel case-study-card">
          <span class="section-tag">Case Study</span>
          <h3>${s.title}</h3>
          <p>${s.summary}</p>
          <div style="margin-top: 1.25rem;">
            <p style="font-size: 0.9rem;">${s.content}</p>
          </div>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error('Error fetching case studies:', e);
  }
}

async function fetchTestimonials() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/testimonials`);
    if (!res.ok) return;
    const reviews = await res.json();
    const grid = document.getElementById('testimonials-grid');

    if (grid && reviews.length > 0) {
      grid.innerHTML = reviews.map(r => `
        <div class="glass-panel testimonial-card">
          <div class="quote-icon">“</div>
          <p class="testimonial-quote">${r.quote}</p>
          <div class="testimonial-author">
            <div class="author-info">
              <h4>${r.client_name}</h4>
              <p>${r.role ? `${r.role}, ` : ''}${r.company || ''}</p>
            </div>
          </div>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error('Error fetching testimonials:', e);
  }
}

async function fetchBlogPosts() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/blog`);
    if (!res.ok) return;
    const posts = await res.json();
    const grid = document.getElementById('blog-grid');

    if (grid && posts.length > 0) {
      grid.innerHTML = posts.map(p => `
        <div class="glass-panel blog-card">
          <div class="blog-date">${p.published_at || 'Recent Post'}</div>
          <h3>${p.title}</h3>
          <p>${p.excerpt}</p>
          <div class="blog-actions">
            <button class="btn btn-secondary read-more-btn" data-post='${JSON.stringify(p).replace(/'/g, "&apos;")}'>
              Read Full Article
            </button>
            ${p.linkedin_url ? `
              <a href="${p.linkedin_url}" target="_blank" rel="noopener" style="font-size: 0.85rem; font-weight: 600;">
                LinkedIn ↗
              </a>
            ` : ''}
          </div>
        </div>
      `).join('');

      // Bind modal read-more buttons
      grid.querySelectorAll('.read-more-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const postData = JSON.parse(e.currentTarget.getAttribute('data-post'));
          openBlogModal(postData);
        });
      });
    }
  } catch (e) {
    console.error('Error fetching blog posts:', e);
  }
}

/* --- Blog Modal Handling --- */
function bindBlogModal() {
  const overlay = document.getElementById('blog-modal-overlay');
  const closeBtn = document.getElementById('modal-close-btn');

  if (closeBtn && overlay) {
    closeBtn.addEventListener('click', () => {
      overlay.classList.remove('active');
    });
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.classList.remove('active');
    });
  }
}

function openBlogModal(post) {
  const overlay = document.getElementById('blog-modal-overlay');
  const titleEl = document.getElementById('modal-post-title');
  const dateEl = document.getElementById('modal-post-date');
  const contentEl = document.getElementById('modal-post-content');
  const linkedinEl = document.getElementById('modal-post-linkedin');

  if (overlay && titleEl && contentEl) {
    titleEl.textContent = post.title;
    if (dateEl) dateEl.textContent = post.published_at || '';
    contentEl.textContent = post.full_content || post.excerpt;

    if (linkedinEl) {
      if (post.linkedin_url) {
        linkedinEl.href = post.linkedin_url;
        linkedinEl.style.display = 'inline-flex';
      } else {
        linkedinEl.style.display = 'none';
      }
    }

    overlay.classList.add('active');
  }
}

/* --- Contact Form Submission --- */
function bindContactForm() {
  const form = document.getElementById('contact-form');
  const toastSuccess = document.getElementById('toast-success');
  const toastError = document.getElementById('toast-error');

  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Reset toasts
    if (toastSuccess) toastSuccess.style.display = 'none';
    if (toastError) toastError.style.display = 'none';

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.textContent : 'Send Message';

    const payload = {
      name: document.getElementById('contact-name').value.trim(),
      email: document.getElementById('contact-email').value.trim(),
      phone: document.getElementById('contact-phone').value.trim(),
      service_interest: document.getElementById('contact-service').value,
      message: document.getElementById('contact-message').value.trim()
    };

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Submitting...';
    }

    try {
      const res = await fetch(`${CONFIG.API_BASE_URL}/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (res.ok) {
        if (toastSuccess) {
          toastSuccess.textContent = data.message || 'Inquiry submitted successfully!';
          toastSuccess.style.display = 'block';
        }
        form.reset();
      } else {
        if (toastError) {
          toastError.textContent = data.error || (data.details ? data.details.join(' ') : 'Submission failed.');
          toastError.style.display = 'block';
        }
      }
    } catch (err) {
      if (toastError) {
        toastError.textContent = 'Network error. Please try again or contact directly via email.';
        toastError.style.display = 'block';
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    }
  });
}

/* Utility to ensure YouTube URLs are embed format */
function sanitizeYouTubeEmbedUrl(url) {
  if (!url) return '';
  if (url.includes('youtube.com/embed/')) return url;
  const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/))([\w-]{11})/);
  return match ? `https://www.youtube.com/embed/${match[1]}` : url;
}
