"""
Email utility functions for sending warning emails.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from src.core.logger import logger
from src.utils.credentials import get_email_credentials

def send_warning_email(subject, body, annotated_image_path, non_annotated_image_path):
    """Send a warning email with detection images.
    
    Args:
        subject: Email subject
        body: Email body text
        annotated_image_path: Path to the annotated image
        non_annotated_image_path: Path to the non-annotated image
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get email credentials from the credentials module
        email_user, email_pass = get_email_credentials()
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_user
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add images
        for image_path in [annotated_image_path, non_annotated_image_path]:
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                    msg.attach(img)
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
            
        logger.info("Warning email sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send warning email: {e}")
        return False

def prepare_and_send_detection_email(timestamp, confidence, annotated_image_path, non_annotated_image_path):
    """Prepare and send a detection email with the given details.
    
    Args:
        timestamp: Detection timestamp
        confidence: Detection confidence score
        annotated_image_path: Path to the annotated image
        non_annotated_image_path: Path to the non-annotated image
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Prepare email details
        subject = "Vespa velutina detected"
        body = f"Dear vespCV user,\n\nA Vespa velutina has been detected on {timestamp} with confidence {confidence}.\n\nBest regards,\nvespCV System"
        
        # Send the email using the existing send_warning_email function
        return send_warning_email(subject, body, annotated_image_path, non_annotated_image_path)
        
    except Exception as e:
        logger.error(f"Failed to prepare and send detection email: {e}")
        return False