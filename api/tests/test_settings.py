from adpa_backend.settings import *

# Test-specific settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

# Disable reCAPTCHA for testing
RECAPTCHA_ENABLED = False

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend' 