import secrets

# Flask secret key (used for sessions, CSRF, etc.)
SECRET_KEY = secrets.token_hex(32)

# Email alert configuration
EMAIL_USER = "s9342902@gmail.com"         # Sender email
EMAIL_PASS = "ncjn fjwj kcwf ocda"        # App password (use env vars in production)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587