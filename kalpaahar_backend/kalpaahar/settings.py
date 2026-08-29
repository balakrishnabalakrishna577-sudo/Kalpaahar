import os
from pathlib import Path
import environ

# ─── Base paths ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# On Render the repo root is /opt/render/project/src/
# Our project structure: repo_root/kalpaahar_backend/ and repo_root/ebooks/ etc.
FRONTEND_DIR = BASE_DIR.parent

# ─── Environment variables ────────────────────────────────────────────────────
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG      = env("DEBUG")

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"]
)

# Render injects RENDER_EXTERNAL_HOSTNAME automatically
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Custom domain
ALLOWED_HOSTS += ["kalpaahar.in", "www.kalpaahar.in"]

# ─── Razorpay ─────────────────────────────────────────────────────────────────
RAZORPAY_KEY_ID         = env("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET     = env("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = env("RAZORPAY_WEBHOOK_SECRET", default="")

# ─── Resend ───────────────────────────────────────────────────────────────────
RESEND_API_KEY = env("RESEND_API_KEY", default="")
EMAIL_FROM     = env("EMAIL_FROM", default="KalpAahar <ebooks@kalpaahar.in>")

# ─── eBooks PDF directory ─────────────────────────────────────────────────────
EBOOKS_PDF_DIR = FRONTEND_DIR / "ebooks"

# ─── Installed apps ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
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
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",     # serve static files in production
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

# ─── Database — SQLite for free tier, easy to swap to Postgres ───────────────
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

# ─── Custom user model ────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"

LOGIN_URL           = "/auth/login/"
LOGIN_REDIRECT_URL  = "/"
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

# ─── Static files — WhiteNoise serves them in production ─────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    FRONTEND_DIR / "css",
    FRONTEND_DIR / "js",
    FRONTEND_DIR / "images",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "https://kalpaahar.in",
    "https://www.kalpaahar.in",
]
CORS_ALLOW_ALL_ORIGINS = DEBUG   # True only in development

# ─── Security (enforced when DEBUG=False) ────────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER    = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT         = True
    SESSION_COOKIE_SECURE       = True
    CSRF_COOKIE_SECURE          = True
    SECURE_HSTS_SECONDS         = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD         = True

# ─── CSRF trusted origins (needed for POST from frontend on custom domain) ───
CSRF_TRUSTED_ORIGINS = [
    "https://kalpaahar.in",
    "https://www.kalpaahar.in",
    "https://*.onrender.com",
]

# ─── Django REST Framework ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
}

# ─── Email ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)