import logging
from collections import defaultdict
from datetime import timedelta

from .rules import RULES, SEVERITY

logger = logging.getLogger(__name__)


def detect(events, rules=RULES, now=None):
    if not events:
        return []

    now = now or max(event["ts"] for event in events)
    alerts = []

    for rule in rules:
        cutoff = now - timedelta(seconds=rule["window_seconds"])
        groups = defaultdict(list)

        for event in events:
            if event["event_type"] != rule["event_type"] or event["ts"] < cutoff:
                continue
            key = tuple(event.get(field, "") for field in rule["group_by"])
            groups[key].append(event)

        for key, group in groups.items():
            distinct_field = rule.get("distinct")
            if distinct_field:
                count = len({
                    event.get(distinct_field)
                    for event in group
                    if event.get(distinct_field)
                })
            else:
                count = len(group)

            if count < rule["threshold"]:
                continue

            alert = {
                "id": rule["id"],
                "name": rule["name"],
                "severity": rule["severity"],
                "severity_label": SEVERITY.get(rule["severity"], "UNKNOWN"),
                "mitre": rule["mitre"],
                "count": count,
                "window_seconds": rule["window_seconds"],
                "key": ", ".join(str(part) for part in key if part) or "global",
                "first_seen": min(event["ts"] for event in group),
                "last_seen": max(event["ts"] for event in group),
            }
            alerts.append(alert)
            logger.warning(
                "alert=%s key=%s count=%s window=%ss",
                alert["id"], alert["key"], count, rule["window_seconds"],
            )

    alerts.sort(key=lambda alert: (alert["severity"], alert["last_seen"]), reverse=True)
    logger.info("detection complete events=%s alerts=%s", len(events), len(alerts))
    return alerts
