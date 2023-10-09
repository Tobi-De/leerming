import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = BASE_DIR / "leerming"

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DJANGO_ENV = env.str("DJANGO_ENV", "dev")
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.forms",
]

THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "schema_viewer",
    "django_q",
    "django_extensions",
    "django_browser_reload",
    "django_htmx",
    "heroicons",
    "widget_tweaks",
    "debug_toolbar",
    "compressor",
    "import_export",
    "template_partials",
    "watson",
]

LOCAL_APPS = [
    "leerming.core",
    "leerming.users",
    "leerming.profiles",
    "leerming.flashcards",
    "leerming.reviews",
]

INSTALLED_APPS = LOCAL_APPS + THIRD_PARTY_APPS + DJANGO_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "watson.middleware.SearchContextMiddleware",
]

if DEBUG:
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": DEBUG,
            "builtins": [
                "heroicons.templatetags.heroicons",
                "django.templatetags.i18n",
                "template_partials.templatetags.partials",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": env.db("DATABASE_URL", default="postgres:///leerming")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [(APPS_DIR / "static")]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_ROOT = str(APPS_DIR / "media")
MEDIA_URL = "/media/"

ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/"

SITE_ID = 1

ACCOUNT_FORMS = {"signup": "leerming.users.forms.SignupForm"}
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "OAUTH_PKCE_ENABLED": True,
        "EMAIL_AUTHENTICATION": True,
    }
}

EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

SUPERUSER_EMAIL = env("DJANGO_SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = env("DJANGO_SUPERUSER_PASSWORD")
FORM_RENDERER = "leerming.core.forms.FormRenderer"

# Django-Q settings
Q_CLUSTER = {
    "name": "DjangORM",
    "workers": 4,
    "timeout": 90,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
    "catch_up": False,
}

# Schema Viewer settings
SCHEMA_VIEWER = {"apps": LOCAL_APPS}

# Django compressor
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = True

# email
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL", default="leerming <noreply@leerming.com>"
)
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

if DJANGO_ENV == "production":
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    # Load cache from CACHE_URL or REDIS_URL
    if "CACHE_URL" in os.environ:
        CACHES = {"default": env.cache("CACHE_URL")}
    elif "REDIS_URL" in os.environ:
        CACHES = {"default": env.cache("REDIS_URL")}

    # Security
    CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS")
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # password validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    # HTTPS only behind a proxy that terminates SSL/TLS
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r"^-/"]
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_PRELOAD = True
    # Only set this to True if you are certain that all subdomains of your domain should be served exclusively via SSL.
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False
    )

    # Databases
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

    # email
    EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
    ANYMAIL = {
        "AMAZON_SES_CLIENT_PARAMS": {
            "aws_access_key_id": env("DJANGO_AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": env("DJANGO_AWS_SECRET_ACCESS_KEY"),
            "region_name": env("DJANGO_AWS_S3_REGION_NAME"),
        }
    }

    # sentry
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        environment=env("SENTRY_ENVIRONMENT", default="production"),
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
        auto_session_tracking=False,
        release="1.0.0",
    )

    # whitenoise
    WHITENOISE_MANIFEST_STRICT = False
