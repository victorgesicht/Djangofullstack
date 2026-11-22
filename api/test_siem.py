from datetime import timedelta
from io import StringIO

from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Bulletins, SecurityEvent
from .siem.collector import collect_events
from .siem.demo import seed_demo_events
from .siem.detection import detect
from .siem.rules import RULES


def event(ts, event_type, src_ip, user, target="login"):
    return {
        "ts": ts,
        "source": "test",
        "event_type": event_type,
        "src_ip": src_ip,
        "user": user,
        "target": target,
        "message": "",
        "severity": 3,
        "severity_label": "HIGH",
    }


@override_settings(ALLOWED_HOSTS=["testserver"])
class DetectionTests(TestCase):

    def test_burst_raises_brute_force_alert(self):
        now = timezone.now()
        events = [
            event(now - timedelta(seconds=i), "auth_failure", "203.0.113.9", "root")
            for i in range(6)
        ]
        alerts = detect(events, RULES, now=now)
        brute = next(alert for alert in alerts if alert["id"] == "BRUTE_FORCE")
        self.assertEqual(brute["count"], 6)
        self.assertEqual(brute["severity_label"], "CRITICAL")
        self.assertEqual(brute["mitre"], "T1110")

    def test_events_outside_window_are_ignored(self):
        now = timezone.now()
        events = [
            event(now - timedelta(hours=2), "auth_failure", "203.0.113.9", "root")
            for _ in range(6)
        ]
        self.assertEqual(detect(events, RULES, now=now), [])

    def test_port_scan_counts_distinct_targets(self):
        now = timezone.now()
        events = [
            event(now - timedelta(seconds=i), "connection", "198.51.100.4", "", str(i))
            for i in range(9)
        ]
        alerts = detect(events, RULES, now=now)
        scan = next(alert for alert in alerts if alert["id"] == "PORT_SCAN")
        self.assertEqual(scan["count"], 9)


@override_settings(ALLOWED_HOSTS=["testserver"])
class TelemetryTests(TestCase):

    def test_failed_login_is_ingested(self):
        self.client.post(reverse("soc_admin:login"), {"username": "root", "password": "wrong"})
        self.assertEqual(
            SecurityEvent.objects.filter(event_type="auth_failure").count(), 1
        )

    def test_admin_audit_is_normalized_into_event_stream(self):
        user = get_user_model().objects.create_superuser("analyst", "a@example.com", "secret123")
        LogEntry.objects.create(
            user=user,
            content_type=ContentType.objects.get_for_model(Bulletins),
            object_id="1",
            object_repr="bulletin",
            action_flag=ADDITION,
            change_message="created",
        )
        events = collect_events()
        self.assertTrue(any(item["event_type"] == "admin_add" for item in events))

    def test_demo_feed_produces_alerts(self):
        seed_demo_events()
        alerts = detect(collect_events(), RULES, now=timezone.now())
        self.assertTrue({alert["id"] for alert in alerts} >= {
            "BRUTE_FORCE", "PORT_SCAN", "WEB_SCAN",
        })

    def test_digest_command_reports_counts(self):
        seed_demo_events()
        output = StringIO()
        call_command("siem_digest", stdout=output)
        self.assertIn("events", output.getvalue())
        self.assertIn("alerts", output.getvalue())


@override_settings(ALLOWED_HOSTS=["testserver"])
class SiemAdminTests(TestCase):

    def setUp(self):
        user = get_user_model().objects.create_superuser("analyst", "a@example.com", "secret123")
        self.client.force_login(user)

    def test_panel_renders_rules_and_branding(self):
        response = self.client.get(reverse("soc_admin:siem"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SOC_CENTRE")
        self.assertContains(response, "BRUTE_FORCE")
        self.assertContains(response, "T1595")

    def test_admin_index_links_to_siem(self):
        response = self.client.get(reverse("soc_admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("soc_admin:siem"))
