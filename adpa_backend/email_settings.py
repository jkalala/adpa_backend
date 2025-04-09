from pathlib import Path
import os

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', '')

# Add these settings for better DNS resolution
EMAIL_TIMEOUT = 30  # Timeout in seconds
EMAIL_USE_LOCALTIME = True

# Email Templates Directory
EMAIL_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / 'templates' / 'email' 