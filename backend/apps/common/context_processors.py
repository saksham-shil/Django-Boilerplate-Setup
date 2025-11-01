from django.conf import settings
from decouple import config


def sentry_dsn(request):
    return {"SENTRY_DSN": settings.SENTRY_DSN}


def commit_sha(request):
    return {"COMMIT_SHA": settings.COMMIT_SHA}


def frontend_domain(request):
    """Add frontend domain to all template contexts"""
    domain = config('FRONTEND_DOMAIN', default='http://localhost:3000')
    if not domain.startswith('http'):
        domain = f'http://{domain}'
    return {'frontend_domain': domain}
