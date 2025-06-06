import os

def get_email_credentials():
    """Retrieve email credentials from ~/.vespcv_credentials."""
    credentials_path = os.path.expanduser('~/.vespcv_credentials')
    
    if not os.path.exists(credentials_path):
        raise FileNotFoundError("Credentials file not found.")
    
    email_user = None
    email_pass = None
    
    with open(credentials_path, 'r') as file:
        for line in file:
            if line.startswith("export EMAIL_USER="):
                email_user = line.split('=')[1].strip().strip('"')
            elif line.startswith("export EMAIL_PASS="):
                email_pass = line.split('=')[1].strip().strip('"')
    
    if not email_user or not email_pass:
        raise ValueError("Email credentials not found in the credentials file.")
    
    return email_user, email_pass
