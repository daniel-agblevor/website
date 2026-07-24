import os
from dotenv import load_dotenv

# Load .env only when not running tests — prevents live credentials from
# bleeding into the test suite and hitting real external services.
if os.environ.get('FLASK_ENV') != 'testing':
    load_dotenv()

def sanitize_database_url(url: str) -> str:
    """Fix Supabase / Heroku postgres:// scheme to postgresql:// required by SQLAlchemy"""
    if not url:
        return "sqlite:///dev.db"
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url

class Config:
    """Base Configuration Object"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "default-jwt-secret-key-change-in-production")
    
    # Database
    RAW_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    SQLALCHEMY_DATABASE_URI = sanitize_database_url(RAW_DATABASE_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supabase Credentials
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    # Email Service Settings (Resend / Brevo)
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
    BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
    NOTIFICATION_EMAIL_TO = os.environ.get("NOTIFICATION_EMAIL_TO", "consultant@example.com")
    NOTIFICATION_EMAIL_FROM = os.environ.get("NOTIFICATION_EMAIL_FROM", "onboarding@resend.dev")

    # Security & CORS
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5000")
    ADMIN_ROUTE_PATH = os.environ.get("ADMIN_ROUTE_PATH", "/admin-portal")

    # Rate Limiting
    RATELIMIT_STORAGE_URI = "memory://"


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing Configuration — all external service credentials blanked out."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Blank all external service URLs/keys so tests never call real APIs
    SUPABASE_URL = ""
    SUPABASE_ANON_KEY = ""
    SUPABASE_SERVICE_ROLE_KEY = ""
    RESEND_API_KEY = ""
    BREVO_API_KEY = ""


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}
