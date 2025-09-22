import sentry_sdk
from decouple import config, Csv
from django_guid.integrations import SentryIntegration as DjangoGUIDSentryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *


DEBUG = False

SECRET_KEY = config("SECRET_KEY")

DATABASES["default"]["ATOMIC_REQUESTS"] = True

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost", cast=Csv())

STATIC_ROOT = base_dir_join("staticfiles")
STATIC_URL = "/static/"

MEDIA_ROOT = base_dir_join("mediafiles")
MEDIA_URL = "/media/"

SERVER_EMAIL = "foo@example.com"

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = config("SENDGRID_USERNAME")
EMAIL_HOST_PASSWORD = config("SENDGRID_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Security
USE_X_FORWARDED_HOST = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=3600, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"


# Celery
# Recommended settings for reliability: https://gist.github.com/fjsj/da41321ac96cf28a96235cb20e7236f6
CELERY_BROKER_URL = config("RABBITMQ_URL", default="") or config("REDIS_URL")
CELERY_RESULT_BACKEND = config("REDIS_URL")
CELERY_SEND_TASK_ERROR_EMAILS = True

# Redbeat https://redbeat.readthedocs.io/en/latest/config.html#redbeat-redis-url
redbeat_redis_url = config("REDBEAT_REDIS_URL", default="")

# Whitenoise
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Django GUID
DJANGO_GUID = {
    "INTEGRATIONS": [
        DjangoGUIDSentryIntegration(),
    ],
}



JS_REVERSE_EXCLUDE_NAMESPACES = ["admin"]

# Sentry
sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()], release=COMMIT_SHA)
