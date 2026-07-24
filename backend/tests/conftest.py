import os
import pytest

# Must be set before importing create_app so config.py skips load_dotenv()
# and real .env credentials never reach the test suite.
os.environ['FLASK_ENV'] = 'testing'

from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    """Create application fixture configured for testing"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def admin_token(app, client):
    """Fixture providing a valid admin JWT token"""
    res = client.post('/api/admin/login', json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    data = res.get_json()
    return data.get("access_token")
