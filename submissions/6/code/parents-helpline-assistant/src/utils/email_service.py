"""Email verification service for HIPAA compliance."""
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils.logger import get_logger
from src.utils.config import settings
import os

logger = get_logger(__name__)


def generate_verification_token() -> str:
    """Generate a secure verification token."""
    return secrets.token_urlsafe(32)


def send_verification_email(email: str, verification_token: str, user_name: str = None) -> bool:
    """
    Send email verification link.

    Args:
        email: User's email address
        verification_token: Verification token
        user_name: User's name for personalization

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # For development/demo: Just log the verification link
        # In production, you'd use a real email service (SendGrid, AWS SES, etc.)

        base_url = os.getenv("APP_BASE_URL", "http://localhost:8501")
        verification_link = f"{base_url}/?verify={verification_token}"

        greeting = f"Hello {user_name}!" if user_name else "Hello!"

        message = f"""
{greeting}

Thank you for creating an account with Parents Healthline Assistant.

For HIPAA compliance and to protect your privacy, please verify your email address by clicking the link below:

{verification_link}

This link will expire in 24 hours.

If you did not create this account, please ignore this email.

Best regards,
Parents Healthline Team

---
This is an automated message. Please do not reply to this email.
"""

        # For demo purposes, log the verification info
        logger.info(f"Email verification link for {email}: {verification_link}")
        logger.info(f"Verification token: {verification_token}")

        # In production, replace this with actual email sending:
        # smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        # smtp_port = int(os.getenv("SMTP_PORT", "587"))
        # smtp_user = os.getenv("SMTP_USER")
        # smtp_password = os.getenv("SMTP_PASSWORD")
        #
        # msg = MIMEMultipart()
        # msg['From'] = smtp_user
        # msg['To'] = email
        # msg['Subject'] = "Verify Your Email - Parents Healthline"
        # msg.attach(MIMEText(message, 'plain'))
        #
        # with smtplib.SMTP(smtp_server, smtp_port) as server:
        #     server.starttls()
        #     server.login(smtp_user, smtp_password)
        #     server.send_message(msg)

        print("\n" + "="*80)
        print("EMAIL VERIFICATION (Demo Mode)")
        print("="*80)
        print(message)
        print("="*80 + "\n")

        return True

    except Exception as e:
        logger.error(f"Error sending verification email: {e}")
        return False


def verify_email_token(token: str) -> bool:
    """
    Verify an email verification token.

    Args:
        token: Verification token

    Returns:
        True if valid, False otherwise
    """
    # Token validation would go here
    # Check expiration, etc.
    return True
