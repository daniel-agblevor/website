import pytest

def test_submit_contact_form_valid(client):
    """Test successful contact form submission"""
    payload = {
        "name": "Kofi Annan",
        "email": "kofi@example.com",
        "phone": "+233201234567",
        "service_interest": "Payroll Automation",
        "message": "Hello, I would like to automate our monthly GRA tax and payroll calculations."
    }
    response = client.post('/api/contact', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "lead_id" in data
    assert "submitted successfully" in data.get("message", "").lower()


def test_submit_contact_form_invalid_email(client):
    """Test contact form with invalid email address"""
    payload = {
        "name": "Kofi Annan",
        "email": "invalid-email-string",
        "message": "This is a test message to verify email validation failure."
    }
    response = client.post('/api/contact', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Validation failed" in data.get("error", "")


def test_submit_contact_form_short_message(client):
    """Test contact form with message shorter than 10 chars"""
    payload = {
        "name": "Kofi Annan",
        "email": "kofi@example.com",
        "message": "Short"
    }
    response = client.post('/api/contact', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Validation failed" in data.get("error", "")
