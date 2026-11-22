import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from ..models import SecurityEvent

logger = logging.getLogger(__name__)


def _client_ip(request):
    if request is None:
        return ""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _record(event_type, request, user, message, severity):
    ip = _client_ip(request)
    try:
        SecurityEvent.objects.create(
            source="django_auth",
            event_type=event_type,
            src_ip=ip,
            user=user,
            target="login",
            message=message,
            severity=severity,
        )
    except Exception:
        logger.exception("telemetry write failed event=%s user=%s", event_type, user)
    else:
        logger.info("event=%s user=%s ip=%s", event_type, user, ip)


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request=None, **kwargs):
    username = (credentials or {}).get("username", "")
    _record("auth_failure", request, username, "Failed authentication attempt", 3)


@receiver(user_logged_in)
def on_logged_in(sender, request, user, **kwargs):
    _record("auth_success", request, user.get_username(), "Session established", 1)


@receiver(user_logged_out)
def on_logged_out(sender, request, user, **kwargs):
    _record("auth_logout", request, user.get_username(), "Session terminated", 1)
