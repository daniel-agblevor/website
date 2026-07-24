import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

def send_new_lead_notification(lead_data: dict) -> bool:
    """
    Sends an email notification to the site owner when a new contact inquiry is submitted.
    Tries Resend API first, then Brevo API if Resend is unavailable.
    """
    resend_key = current_app.config.get("RESEND_API_KEY")
    brevo_key = current_app.config.get("BREVO_API_KEY")
    to_email = current_app.config.get("NOTIFICATION_EMAIL_TO")
    from_email = current_app.config.get("NOTIFICATION_EMAIL_FROM")

    subject = f"New HR Automation Inquiry: {lead_data.get('name')} - {lead_data.get('service_interest', 'General')}"
    html_content = f"""
    <h2>New Client Inquiry Received</h2>
    <p><strong>Name:</strong> {lead_data.get('name')}</p>
    <p><strong>Email:</strong> <a href="mailto:{lead_data.get('email')}">{lead_data.get('email')}</a></p>
    <p><strong>Phone:</strong> {lead_data.get('phone', 'N/A')}</p>
    <p><strong>Service Interest:</strong> {lead_data.get('service_interest', 'N/A')}</p>
    <p><strong>Message:</strong></p>
    <blockquote style="background: #f4f4f5; padding: 12px; border-left: 4px solid #48CAE4;">
        {lead_data.get('message')}
    </blockquote>
    <p><em>Submitted via HR Systems & Automation Consulting Website.</em></p>
    """

    # Try Resend API
    if resend_key:
        try:
            res = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": from_email,
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content
                },
                timeout=10
            )
            if res.status_code in [200, 201]:
                logger.info(f"Resend notification email sent successfully for lead {lead_data.get('email')}")
                return True
            else:
                logger.warning(f"Resend notification failed with status {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Error sending Resend email: {e}")

    # Fallback to Brevo API
    if brevo_key:
        try:
            res = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": brevo_key,
                    "Content-Type": "application/json"
                },
                json={
                    "sender": {"email": from_email, "name": "HR Systems Web Bot"},
                    "to": [{"email": to_email}],
                    "subject": subject,
                    "htmlContent": html_content
                },
                timeout=10
            )
            if res.status_code in [200, 201]:
                logger.info(f"Brevo notification email sent successfully for lead {lead_data.get('email')}")
                return True
            else:
                logger.warning(f"Brevo notification failed with status {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Error sending Brevo email: {e}")

    logger.warning("No email provider API key configured or all email sends failed. Inquiry saved to database.")
    return False
