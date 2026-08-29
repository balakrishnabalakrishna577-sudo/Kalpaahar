import os
from pathlib import Path
import environ

# ─── Base paths ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Frontend static site lives one level up from the backend folder
FRONTEND_DIR = BASE_DIR.parent

# ─── Environment variables ────────────────────────────────────────────────────
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG      = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# ─── Razorpay ─────────────────────────────────────────────────────────────────
RAZORPAY_KEY_ID      = env("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET  = env("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = env("RAZORPAY_WEBHOOK_SECRET", default="")

# ─── Resend ───────────────────────────────────────────────────────────────────
RESEND_API_KEY = env("RESEND_API_KEY", default="")
EMAIL_FROM     = env("EMAIL_FROM", default="KalpAahar <ebooks@kalpaahar.in>")

# ─── eBooks PDF directory ─────────────────────────────────────────────────────
EBOOKS_PDF_DIR = FRONTEND_DIR / "ebooks"

# ─── Installed apps ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Custom admin theme must be before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Local apps
    "accounts",
    "payments",
    "ebooks",
]

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",          # must be first
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kalpaahar.urls"

# ─── Templates ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "kalpaahar.wsgi.application"

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ─── Custom user model ────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"

# ─── Auth redirects ───────────────────────────────────────────────────────────
LOGIN_URL          = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ─── Password validators ──────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Internationalisation ─────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Asia/Kolkata"
USE_I18N      = True
USE_TZ        = True

# ─── Static & media ───────────────────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Serve the frontend's own css/js/images as static files
STATICFILES_DIRS = [
    FRONTEND_DIR / "css",
    FRONTEND_DIR / "js",
    FRONTEND_DIR / "images",
]

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True   # development only

# ─── Django REST Framework ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# ─── Email (console for dev — swap for SMTP / Resend in production) ───────────
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
