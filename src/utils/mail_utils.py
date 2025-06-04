"""
Email utility functions for the vespCV application.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from src.core.logger import logger
import tkinter as tk
from tkinter import messagebox

def check_email_credentials():
    """Check if email credentials are properly set in environment variables.
    
    Returns:
        tuple: (bool, str) - (credentials_valid, error_message)
    """
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    
    if not sender_email or not password:
        error_msg = (
            "Email credentials not found in environment variables.\n\n"
            "Please add the following to your ~/.bashrc file:\n\n"
            'export EMAIL_USER="your_email@gmail.com"\n'
            'export EMAIL_PASS="your_email_password"\n\n'
            "Then run: source ~/.bashrc"
        )
        return False, error_msg
    return True, ""

def send_warning_email(subject, body, annotated_image_path, non_annotated_image_path):
    """Send a warning email with detection images.
    
    Args:
        subject (str): Email subject
        body (str): Email body text
        annotated_image_path (str): Path to the annotated image
        non_annotated_image_path (str): Path to the non-annotated image
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Check credentials first
        credentials_valid, error_msg = check_email_credentials()
        if not credentials_valid:
            logger.error(error_msg)
            messagebox.showerror("Email Configuration Error", error_msg)
            return False

        # Get email credentials from environment variables
        sender_email = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")
        receiver_email = os.getenv("EMAIL_RECIPIENT", sender_email)  # Default to sender if no recipient specified

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
            return True

    except Exception as e:
        error_msg = f"Failed to send warning email: {str(e)}"
        logger.error(error_msg)
        messagebox.showerror("Email Error", error_msg)
        return False

print("EMAIL_USER:", os.getenv("EMAIL_USER"))
print("EMAIL_PASS:", os.getenv("EMAIL_PASS"))