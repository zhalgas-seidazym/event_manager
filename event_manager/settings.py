"""
Django Settings for Event Manager with MinIO Storage
Elegantly configured for development with Docker
"""

import os
from pathlib import Path
import sys
from datetime import timedelta

# Flush output immediately for Docker logs
sys.stdout.flush()

# --------------------------
# Path Configuration
# --------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------
# Core Django Configuration
# --------------------------
SECRET_KEY = os.getenv('DJANGO_SECRET', 'django-insecure-dev-key-please-change-me')
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'eventify.adminconfig.EventifyAdminConfig',  # Custom admin config
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',  # S3/MinIO storage backend
    'drf_spectacular',
    'rest_framework',
    'rest_framework.authtoken',
    'eventify',  # Your custom app
    'corsheaders',
    'django_extensions',  # ← добавь вот сюда
    'debug_toolbar',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Add spectacular settings (optional)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API Title',
    'DESCRIPTION': 'Detailed description of your API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # Set to True if you want to serve the schema too
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
}

INTERNAL_IPS = [
    # локальный IP, если вы используете Docker, можно использовать localhost или 127.0.0.1
    "127.0.0.1",
]

ROOT_URLCONF = 'event_manager.urls'
WSGI_APPLICATION = 'event_manager.wsgi.application'
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:63343"]

# --------------------------
# Database Configuration
# --------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'mydb'),
        'USER': os.getenv('DATABASE_USER', 'admin'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'root'),
        'HOST': os.getenv('DATABASE_HOST', 'postgres_db'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

# --------------------------
# MinIO Storage Configuration
# --------------------------
MINIO_PORT = os.getenv('MINIO_PORT', 9000)
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'eventify')

# Storage Backend Settings
STORAGES = {
    "default": {
        "BACKEND": "eventify.storage.MediaStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

AWS_ACCESS_KEY_ID = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
AWS_SECRET_ACCESS_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')
AWS_STORAGE_BUCKET_NAME = MINIO_BUCKET
AWS_S3_ENDPOINT_URL = f'http://minio:{MINIO_PORT}'  # Internal Docker network



# Security and Behavior Settings
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_USE_SSL = False
AWS_S3_SECURE_URLS = False
AWS_S3_ADDRESSING_STYLE = 'path'

# Media URL Configuration
MEDIA_URL = f'http://localhost:{MINIO_PORT}/{AWS_STORAGE_BUCKET_NAME}/'

# Security Settings to prevent HTTPS redirection
SECURE_SSL_REDIRECT = False


# --------------------------
# Static Files Configuration
# --------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --------------------------
# Internationalization
# --------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --------------------------
# Templates Configuration
# --------------------------
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'django.template.context_processors.media',
        ],
    },
}]

# --------------------------
# Password Validation
# --------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------
# Default Primary Key
# --------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'