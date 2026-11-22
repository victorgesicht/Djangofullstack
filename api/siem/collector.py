from datetime import timedelta

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.utils import timezone

from ..models import SecurityEvent
from .rules import SEVERITY

ADMIN_EVENT_TYPES = {
    ADDITION: "admin_add",
    CHANGE: "admin_change",
    DELETION: "admin_delete",
}

ADMIN_SEVERITY = {
    ADDITION: 1,
    CHANGE: 1,
    DELETION: 3,
}


def _admin_events(cutoff):
    return [
        {
            "ts": entry.action_time,
            "source": "admin_audit",
            "event_type": ADMIN_EVENT_TYPES.get(entry.action_flag, "admin_change"),
            "src_ip": "",
            "user": entry.user.get_username() if entry.user else "system",
            "target": entry.object_repr[:200],
            "message": entry.change_message,
            "severity": ADMIN_SEVERITY.get(entry.action_flag, 1),
            "severity_label": SEVERITY.get(ADMIN_SEVERITY.get(entry.action_flag, 1), "UNKNOWN"),
        }
        for entry in LogEntry.objects.filter(action_time__gte=cutoff).select_related("user")
    ]


def collect_events(hours=24):
    cutoff = timezone.now() - timedelta(hours=hours)
    events = [event.as_event() for event in SecurityEvent.objects.filter(ts__gte=cutoff)]
    events.extend(_admin_events(cutoff))
    events.sort(key=lambda event: event["ts"], reverse=True)
    return events
