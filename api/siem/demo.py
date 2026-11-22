from datetime import timedelta

from django.utils import timezone

from ..models import SecurityEvent


def seed_demo_events():
    now = timezone.now()
    rows = []

    def add(seconds_ago, event_type, src_ip, user, target, message, severity):
        rows.append(SecurityEvent(
            ts=now - timedelta(seconds=seconds_ago),
            source="simulator",
            event_type=event_type,
            src_ip=src_ip,
            user=user,
            target=target,
            message=message,
            severity=severity,
        ))

    for offset in range(7):
        add(240 - offset * 8, "auth_failure", "203.0.113.42", "root", "login", "Invalid password", 3)

    for index, port in enumerate((21, 22, 23, 25, 53, 80, 110, 143, 443, 445)):
        add(180 - index * 6, "connection", "198.51.100.77", "", str(port), "TCP connect", 2)

    for index, path in enumerate(("/admin", "/.env", "/wp-login.php", "/phpinfo.php", "/.git/config", "/actuator", "/backup.sql", "/config.json", "/admin.php", "/shell")):
        add(300 - index * 10, "http_404", "192.0.2.15", "", path, "HTTP 404", 2)

    add(30, "auth_success", "10.0.0.4", "analyst", "login", "Session established", 1)

    SecurityEvent.objects.bulk_create(rows)
    return len(rows)
