# config/settings/development.py

from .base import *  # noqa

DEBUG = True

# Relaxed CORS for local development
CORS_ALLOW_ALL_ORIGINS = True

# Use console email backend during dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Show SQL queries in development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}