import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passkey import PassKey
import logging

# Gmail credentials from environment variables for security
SENDER_EMAIL = PassKey.SENDER_EMAIL
EMAIL_PASSWORD = PassKey.EMAIL_PASSWORD

def send_email(receiver_email: str, subject: str, body: str) -> bool:
    """
    Send an email using Gmail SMTP server.
    Args:
        receiver_email (str): Recipient email address.
        subject (str): Email subject.
        body (str): Email body text.

    """
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
        logging.info(f"Email sent successfully to {receiver_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        logging.error("Authentication failed. Use an App Password (not your Gmail login password).")
        return False
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return False
