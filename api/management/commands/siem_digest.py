import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.siem.collector import collect_events
from api.siem.detection import detect
from api.siem.rules import RULES

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run detection over the last 24h and log a summary."

    def handle(self, *args, **options):
        events = collect_events(hours=24)
        alerts = detect(events, RULES, now=timezone.now())

        self.stdout.write(f"{len(events)} events · {len(alerts)} alerts")
        for alert in alerts:
            logger.warning(
                "%s key=%s count=%s severity=%s",
                alert["id"], alert["key"], alert["count"], alert["severity_label"],
            )
