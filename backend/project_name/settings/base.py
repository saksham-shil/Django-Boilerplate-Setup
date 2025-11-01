import os
import sys

from decouple import config, Csv
from dj_database_url import parse as db_url

from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def base_dir_join(*args):
    return os.path.join(BASE_DIR, *args)


SITE_ID = 1

DEBUG = config('DEBUG', default=False, cast=bool)

ADMINS = [(config('ADMIN_NAME', default='Admin'), config('ADMIN_EMAIL', default='admin@example.com'))]

AUTH_USER_MODEL = "users.User"

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost", cast=Csv())

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:8000,http://127.0.0.1:8000",
    cast=Csv()
)

# Base URL for generating absolute URLs (media files, pagination, etc.)
BASE_URL = config("BASE_URL", default="http://localhost:8000")

DATABASES = {
    "default": config("DATABASE_URL", cast=db_url),
}

PRE_INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_js_reverse",
    "rest_framework",
    "drf_spectacular",
    "defender",
    "django_guid",
]

EXTERNAL_APPS = [
'corsheaders',
]

# Only add debug toolbar when DEBUG is True and not running tests
RUNNING_TESTS = 'test' in sys.argv
if DEBUG and not RUNNING_TESTS:
    EXTERNAL_APPS.append('debug_toolbar')

LOCAL_APPS = [
    "apps.common",
    "apps.common.audit",
    "apps.users",
]

INSTALLED_APPS = PRE_INSTALLED_APPS + EXTERNAL_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "defender.middleware.FailedLoginMiddleware",
    "django_guid.middleware.guid_middleware",
    "{{ project_name }}.middleware.LoggingMiddleware",
]

# Only add debug toolbar middleware when DEBUG is True and not running tests
if DEBUG and not RUNNING_TESTS:
    MIDDLEWARE.insert(2, 'debug_toolbar.middleware.DebugToolbarMiddleware')
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173", cast=Csv())


ROOT_URLCONF = "{{ project_name }}.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [base_dir_join("templates")],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.common.context_processors.sentry_dsn",
                "apps.common.context_processors.commit_sha",
                "apps.common.context_processors.frontend_domain",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
        },
    },
]

WSGI_APPLICATION = "{{ project_name }}.wsgi.application"

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        'rest_framework_simplejwt.authentication.JWTAuthentication', 
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.common.api_responses.exception_handler.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardPagination",
    "PAGE_SIZE": config('REST_FRAMEWORK_PAGE_SIZE', default=10, cast=int),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': config('THROTTLE_ANON', default='60/hour'),      # Anonymous users
        'user': config('THROTTLE_USER', default='1000/day'),     # Authenticated users
        'burst': config('THROTTLE_BURST', default='60/min'),     # For burst operations
    }
}

SIMPLE_JWT = {
    # Token lifetimes
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "Django Boilerplate API",
    "DESCRIPTION": "API Schema for Django Boilerplate Application",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True


USE_TZ = True
# STATIC_URL  = "/static/"
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]
# STATIC_ROOT = BASE_DIR / "staticfiles"   # for collectstatic in production


# Redis Configuration with Authentication
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@result:6379/0"
else:
    REDIS_URL = config("REDIS_URL", default="redis://result:6379/0")

# Celery
# Recommended settings for reliability: https://gist.github.com/fjsj/da41321ac96cf28a96235cb20e7236f6
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_ACKS_LATE = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_TRANSPORT_OPTIONS = {"confirm_publish": True, "confirm_timeout": 5.0}
CELERY_BROKER_POOL_LIMIT = config("CELERY_BROKER_POOL_LIMIT", cast=int, default=1)
CELERY_BROKER_CONNECTION_TIMEOUT = config(
    "CELERY_BROKER_CONNECTION_TIMEOUT", cast=float, default=30.0
)
CELERY_REDIS_MAX_CONNECTIONS = config(
    "CELERY_REDIS_MAX_CONNECTIONS", cast=lambda v: int(v) if v else None, default=None
)
CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT = config(
    "CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT", cast=bool, default=True
)
CELERY_TASK_REJECT_ON_WORKER_LOST = config(
    "CELERY_TASK_REJECT_ON_WORKER_LOST", cast=bool, default=False
)
CELERY_WORKER_PREFETCH_MULTIPLIER = config("CELERY_WORKER_PREFETCH_MULTIPLIER", cast=int, default=1)
CELERY_WORKER_CONCURRENCY = config(
    "CELERY_WORKER_CONCURRENCY", cast=lambda v: int(v) if v else None, default=None
)
CELERY_WORKER_MAX_TASKS_PER_CHILD = config(
    "CELERY_WORKER_MAX_TASKS_PER_CHILD", cast=int, default=1000
)
CELERY_WORKER_SEND_TASK_EVENTS = config("CELERY_WORKER_SEND_TASK_EVENTS", cast=bool, default=True)
CELERY_EVENT_QUEUE_EXPIRES = config("CELERY_EVENT_QUEUE_EXPIRES", cast=float, default=60.0)
CELERY_EVENT_QUEUE_TTL = config("CELERY_EVENT_QUEUE_TTL", cast=float, default=5.0)

# Sentry
SENTRY_DSN = config("SENTRY_DSN", default="")
COMMIT_SHA = config("RENDER_GIT_COMMIT", default="")

# Fix for Safari 12 compatibility issues, please check:
# https://github.com/vintasoftware/safari-samesite-cookie-issue
CSRF_COOKIE_SAMESITE = None
SESSION_COOKIE_SAMESITE = None

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# All available policies are listed at:
# https://github.com/w3c/webappsec-permissions-policy/blob/main/features.md
# Empty list means the policy is disabled
PERMISSIONS_POLICY = {
    "accelerometer": [],
    "camera": [],
    "display-capture": [],
    "encrypted-media": [],
    "geolocation": [],
    "gyroscope": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
    "xr-spatial-tracking": [],
}

# Django-CSP
CSP_INCLUDE_NONCE_IN = ["script-src", "style-src", "font-src"]
CSP_SCRIPT_SRC = [
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    "https://browser.sentry-cdn.com",
    # drf-spectacular UI (Swagger and ReDoc)
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/",
    "https://cdn.jsdelivr.net/npm/redoc@latest/",
    "blob:",
] + [f"*{host}" if host.startswith(".") else host for host in ALLOWED_HOSTS]
CSP_CONNECT_SRC = [
    "'self'",
    "*.sentry.io",
] + [f"*{host}" if host.startswith(".") else host for host in ALLOWED_HOSTS]
CSP_STYLE_SRC = [
    "'self'",
    "'unsafe-inline'",
    # drf-spectacular UI (Swagger and ReDoc)
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/",
    "https://cdn.jsdelivr.net/npm/redoc@latest/",
    "https://fonts.googleapis.com",
]
CSP_FONT_SRC = [
    "'self'",
    "'unsafe-inline'",
    # drf-spectacular UI (Swagger and ReDoc)
    "https://fonts.gstatic.com",
] + [f"*{host}" if host.startswith(".") else host for host in ALLOWED_HOSTS]
CSP_IMG_SRC = [
    "'self'",
    # drf-spectacular UI (Swagger and ReDoc)
    "data:",
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/",
    "https://cdn.redoc.ly/redoc/",
]

# Django-defender
DEFENDER_LOGIN_FAILURE_LIMIT = config('DEFENDER_LOGIN_FAILURE_LIMIT', default=3, cast=int)
DEFENDER_COOLOFF_TIME = config('DEFENDER_COOLOFF_TIME', default=300, cast=int)  # seconds
DEFENDER_LOCKOUT_TEMPLATE = "defender/lockout.html"
DEFENDER_REDIS_URL = REDIS_URL


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "correlation_id": {"()": "django_guid.log_filters.CorrelationId"},
    },
    "formatters": {
        "standard": {
            "format": "%(levelname)-8s [%(asctime)s] [%(correlation_id)s] %(name)s: %(message)s"
        },
        "api_request": {
            "format": "%(message)s"  # Format in middleware
        },
    },
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": ["correlation_id"],
        },
        "django_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/django.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,   #Keep 5 files
            "formatter": "standard",
            "filters": ["correlation_id"],
        },
        "api_requests_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/api_requests.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5, #Keep 5 files 
            "formatter": "api_request",
            "filters": ["correlation_id"],
        },
        "api_errors_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/api_errors.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "formatter": "api_request",
            "filters": ["correlation_id"],
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "django_file"],
            "level": "INFO"
        },
        "celery": {
            "handlers": ["console", "django_file"], 
            "level": "INFO"
        },
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
        "django.request": {
            "handlers": ["mail_admins", "django_file"],
            "level": "ERROR",
            "propagate": True,
        },
        "django_guid": {
            "handlers": ["console", "django_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "api_requests": {
            "handlers": ["api_requests_file"],
            "level": "INFO",
            "propagate": False,
        },
        "api_errors": {
            "handlers": ["api_errors_file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER', default='')
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=20, cast=int)

# Django Debug Toolbar - Only when DEBUG is True
if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }

