"""
Django settings for config project.
"""
from pathlib import Path
import environ

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Load .env file ===
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / '.env')

# === Security ===
SECRET_KEY = env('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']

# === Installed Apps ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'channels',

    'users',
    'documents',
    'nlp_engine',
    'notifications',
]

# === Middleware ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# === Templates ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# === Channels ===
ASGI_APPLICATION = 'config.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# === Database (SQLite) ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# === Password validation ===
AUTH_PASSWORD_VALIDATORS = []

# === Internationalization ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# === Static files ===
STATIC_URL = 'static/'

# === Default primary key field ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === Email (console فقط) ===
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# === Twilio (disabled) ===
TWILIO_SID = ''
TWILIO_TOKEN = ''
TWILIO_PHONE = ''

# === App Settings (dummy values) ===
APP_BASE_URL = "http://127.0.0.1:8000"
INACTIVITY_THRESHOLD_DAYS = 30
GRACE_PERIOD_DAYS = 7
VERIFICATION_EXPIRY_HOURS = 24

# === Storage (local بدل AWS) ===
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# === REST Framework ===
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # عشان ما يقفل عليك
    ],
}

# === Encryption Key (dummy) ===
FIELD_ENCRYPTION_KEY = "Tsh2JkuRgBWfdhJG3XDmV9ly4GrAsjKlNiLoOHM2eTk="

# === Security (Production only) ===
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True