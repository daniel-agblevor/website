# HR Systems & Automation Consulting Website & API Backend

A high-performance, responsive consulting portfolio website and REST API backend for an HR Systems & Automation consultant based in Accra, Ghana.

## Repository Structure

```
.
├── docs/                       # ── Frontend (GitHub Pages root) ──────────────
│   ├── index.html              # Public landing page
│   ├── css/
│   │   └── styles.css          # Glassmorphism design system & CSS variables
│   ├── js/
│   │   ├── config.js           # API base URL (switches local ↔ production)
│   │   ├── animations.js       # GSAP + Lenis smooth scroll initializer
│   │   ├── slideshow.js        # Photo carousel component (up to 15 images)
│   │   └── main.js             # Theme toggle, API fetch, blog modal, contact form
│   └── admin/                  # Private unlisted admin panel
│       ├── index.html          # Admin console UI
│       └── admin.js            # Auth, leads table, feature toggles & CRUD
├── backend/                    # ── Backend (Render root directory) ────────────
│   ├── app/
│   │   ├── __init__.py         # Application factory (create_app)
│   │   ├── config.py           # Config classes & Supabase URL sanitizer
│   │   ├── extensions.py       # SQLAlchemy, CORS, Limiter instances
│   │   ├── models.py           # SQLAlchemy models (Lead, Portfolio, etc.)
│   │   ├── auth.py             # JWT generation & Supabase Auth verification
│   │   ├── routes/
│   │   │   ├── public_api.py   # Public REST endpoints
│   │   │   └── admin_api.py    # JWT-protected admin endpoints
│   │   └── services/
│   │       └── email_service.py# Resend / Brevo email notification service
│   ├── tests/
│   │   ├── conftest.py         # Pytest fixtures (SQLite in-memory)
│   │   ├── test_contact.py     # Contact form & validation tests
│   │   ├── test_features.py    # Feature flag endpoint tests
│   │   └── test_admin.py       # JWT auth & lead management tests
│   ├── .env.example            # Sample environment variables (no real values)
│   ├── requirements.txt        # Python dependencies
│   ├── run.py                  # Local development server
│   └── wsgi.py                 # Render production WSGI entry point
├── .gitignore                  # Excludes .env, venv/, __pycache__/, *.db
└── README.md                   # This file
```

> [!IMPORTANT]
> **Never commit `.env`**. Copy `backend/.env.example` to `backend/.env` and fill in your real values. The `.gitignore` at the repo root excludes `.env` and `.env.*` in all subdirectories.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla HTML5, CSS3, JavaScript (ES6+) |
| **Animations** | GSAP + ScrollTrigger, Lenis smooth scroll |
| **Backend** | Python Flask (application factory pattern) |
| **Database** | Supabase Postgres via SQLAlchemy + psycopg2 |
| **Auth** | Supabase Auth → custom Flask JWT middleware |
| **Email** | Resend API (Brevo fallback) |
| **Frontend hosting** | GitHub Pages (`/docs` folder) |
| **Backend hosting** | Render (Starter plan, always-on) |

---

## Local Development Setup

### Prerequisites
- Python 3.10+
- Git

### 1. Clone & configure environment

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# Copy example env and fill in your values
cp backend/.env.example backend/.env
# Edit backend/.env with your Supabase, Resend, and other credentials
```

### 2. Install Python dependencies

```bash
cd backend
py -m pip install --user -r requirements.txt
```

### 3. Run the Flask development server

```bash
# From the backend/ directory
py run.py
```

- **Public site**: http://localhost:5000
- **Admin panel**: http://localhost:5000/`<your ADMIN_ROUTE_PATH>`

> In development, SQLite (`dev.db`) is used automatically when `DATABASE_URL` is not set. The database tables and seed data are created on first run.

### 4. Run automated tests

```bash
# From the backend/ directory
$env:PYTHONPATH = "."; & "path\to\pytest.exe" -v
# Or on macOS/Linux:
PYTHONPATH=. pytest -v
```

Expected: **10 passed** (contact form, feature flags, JWT auth, lead management).

---

## Production Deployment

### Architecture

```
  GitHub Pages (/docs)          Render Web Service (/backend)
  ─────────────────────         ─────────────────────────────
  docs/index.html          ──►  Flask API  ──►  Supabase Postgres
  docs/admin/index.html         (gunicorn)       Supabase Auth
```

---

### Step 1: Set Up Supabase

1. Log in to [supabase.com](https://supabase.com) and create a new project.
2. Go to **Settings → Database → Connection string** and copy the URI (`postgres://...`).
3. Go to **Settings → API** and copy `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY`.
4. Go to **Authentication → Users** and create an admin user with your email + password.

---

### Step 2: Deploy Backend to Render

1. Log in to [render.com](https://render.com) → **New + → Web Service**.
2. Connect your GitHub repository.
3. Configure the service:

   | Setting | Value |
   |---|---|
   | **Name** | `hr-systems-api` |
   | **Root Directory** | `backend` |
   | **Environment** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn wsgi:app` |
   | **Instance Type** | Starter (or Free) |

4. Add **Environment Variables** in the Render dashboard:

   | Key | Value |
   |---|---|
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | *(generate a long random string)* |
   | `JWT_SECRET_KEY` | *(generate a long random string)* |
   | `DATABASE_URL` | *(Supabase connection string)* |
   | `SUPABASE_URL` | `https://your-project.supabase.co` |
   | `SUPABASE_ANON_KEY` | *(from Supabase Settings → API)* |
   | `SUPABASE_SERVICE_ROLE_KEY` | *(from Supabase Settings → API)* |
   | `RESEND_API_KEY` | *(from resend.com)* |
   | `NOTIFICATION_EMAIL_TO` | `your-email@domain.com` |
   | `NOTIFICATION_EMAIL_FROM` | `onboarding@resend.dev` |
   | `FRONTEND_URL` | `https://yourusername.github.io` |
   | `ADMIN_ROUTE_PATH` | `/your-secret-admin-slug` |

5. Deploy. Note your live Render URL (e.g. `https://hr-systems-api.onrender.com`).

---

### Step 3: Update Frontend API URL

Open `docs/js/config.js` and set your Render URL:

```javascript
PRODUCTION_API_URL: 'https://hr-systems-api.onrender.com'
```

Commit and push.

---

### Step 4: Deploy Frontend to GitHub Pages

1. In your GitHub repository: **Settings → Pages**
2. Configure:

   | Setting | Value |
   |---|---|
   | **Source** | Deploy from a branch |
   | **Branch** | `main` |
   | **Folder** | `/docs` |

3. Save. GitHub Pages publishes at `https://yourusername.github.io/repository-name/`.

---

## Admin Panel Access

The private admin panel is accessible at:
```
https://yourusername.github.io/repository-name/admin/
```
(Served by GitHub Pages from `docs/admin/index.html`)

> [!NOTE]
> The admin UI calls the Render API, which validates the JWT on every protected request. The Supabase Auth login gate is always enforced — route obscurity is a secondary measure only.

---

## Feature Flags

Toggle public site sections on/off without a code redeploy:

1. Open the admin panel and log in.
2. Navigate to **Feature Toggles**.
3. Flip switches for **Services**, **Portfolio**, **Case Studies**, **Testimonials**, or **Blog**.
4. The public site immediately hides disabled sections and skips their API calls.

---

## Security Notes

- `.env` and `.env.*` are excluded by `.gitignore` — **never commit real credentials**.
- `SUPABASE_SERVICE_ROLE_KEY` bypasses Postgres RLS — keep it strictly server-side in Render env vars.
- JWT tokens for admin sessions expire after 12 hours.
- The contact form endpoint is rate-limited to **5 requests per minute** per IP.
- CORS is restricted to `FRONTEND_URL` only (not `*`) for all `/api/*` routes.
