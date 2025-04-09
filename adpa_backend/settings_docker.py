from .settings import *
from .email_settings import *
import os
from urllib.parse import urlparse

# Get database settings from environment variable
db_url = urlparse(os.environ.get('DATABASE_URL'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_url.path[1:],
        'USER': db_url.username,
        'PASSWORD': db_url.password,
        'HOST': db_url.hostname,
        'PORT': db_url.port or '5432',
    }
}

# Update secret key from environment
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# Update debug mode from environment
DEBUG = bool(int(os.environ.get('DEBUG', '0')))

# Allow all hosts in Docker environment
ALLOWED_HOSTS = ['*']

# Update CORS settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Use console backend for development to avoid DNS issues
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production, uncomment these settings
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL') 

# Email Templates Directory
TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'templates'))

# Create email templates directory if it doesn't exist
EMAIL_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# reCAPTCHA settings
RECAPTCHA_ENABLED = True
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
RECAPTCHA_SCORE_THRESHOLD = 0.5 