from django.test import TestCase, override_settings
from django.urls import reverse

from .models import TrainingOffer, TrainingOffering


@override_settings(ALLOWED_HOSTS=["testserver"])
class TrainingPageTests(TestCase):

    def test_page_lists_tracks_and_converted_price(self):
        response = self.client.get(reverse("training"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "KES 2,000")
        self.assertContains(response, "15.50")
        self.assertContains(response, "Active Directory Attack Paths")

    def test_offer_submission_strips_html(self):
        offering = TrainingOffering.objects.get(slug="osint")
        response = self.client.post(reverse("training"), {
            "callsign": "<b>0xr3d</b>",
            "contact": "op@example.com<script>alert(1)</script>",
            "kind": TrainingOffer.Kind.VOUCHER,
            "link": "https://forum.example/t/1",
            "message": "<img src=x onerror=alert(1)> voucher worth two hours",
            "offering_slug": offering.slug,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        offer = TrainingOffer.objects.get()
        self.assertEqual(offer.callsign, "0xr3d")
        self.assertEqual(offer.contact, "op@example.com")
        self.assertNotIn("<img", offer.message)
        self.assertEqual(offer.offering, offering)

    def test_link_scheme_is_restricted(self):
        response = self.client.post(reverse("training"), {
            "callsign": "0xr3d",
            "contact": "op@example.com",
            "kind": TrainingOffer.Kind.FORUM,
            "link": "javascript:alert(1)",
            "message": "forum link for the squad",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrainingOffer.objects.count(), 0)
        self.assertContains(response, "Enter a valid URL")

    def test_honeypot_silently_drops_bots(self):
        response = self.client.post(reverse("training"), {
            "callsign": "bot",
            "contact": "bot@example.com",
            "kind": TrainingOffer.Kind.OTHER,
            "message": "buy cheap backlinks now",
            "website": "https://spam.example",
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrainingOffer.objects.count(), 0)

    def test_repeat_submission_is_throttled(self):
        payload = {
            "callsign": "0xr3d",
            "contact": "op@example.com",
            "kind": TrainingOffer.Kind.COLLAB,
            "message": "collab on a retired lab build",
        }
        self.client.post(reverse("training"), payload)
        self.client.post(reverse("training"), payload)

        self.assertEqual(TrainingOffer.objects.count(), 1)
