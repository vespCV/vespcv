"""
Email utility functions for the vespCV application.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from src.core.logger import logger

def send_warning_email(subject, body, annotated_image_path, non_annotated_image_path):
    """Send a warning email with detection images.
    
    Args:
        subject (str): Email subject
        body (str): Email body text
        annotated_image_path (str): Path to the annotated image
        non_annotated_image_path (str): Path to the non-annotated image
    """
    try:
        # Get email credentials from environment variables
        sender_email = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")
        receiver_email = os.getenv("EMAIL_RECIPIENT", "recipient_email@example.com")

        if not sender_email or not password:
            logger.error("Email credentials not found in environment variables")
            return

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEText(body, 'plain'))

        # Attach images if they exist
        if os.path.exists(annotated_image_path):
            with open(annotated_image_path, 'rb') as f:
                msg.attach(MIMEImage(f.read(), name=os.path.basename(annotated_image_path)))
        else:
            logger.warning(f"Annotated image not found: {annotated_image_path}")

        if os.path.exists(non_annotated_image_path):
            with open(non_annotated_image_path, 'rb') as f:
                msg.attach(MIMEImage(f.read(), name=os.path.basename(non_annotated_image_path)))
        else:
            logger.warning(f"Non-annotated image not found: {non_annotated_image_path}")

        # Connect to the server and send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
            logger.info("Warning email sent successfully")

    except Exception as e:
        logger.error(f"Failed to send warning email: {e}")