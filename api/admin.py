import logging

from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone

from .models import Bulletins, Comment, SecurityEvent, TrainingOffer, TrainingOffering
from .siem.collector import collect_events
from .siem.demo import seed_demo_events
from .siem.detection import detect
from .siem.rules import RULES

logger = logging.getLogger(__name__)
WINDOW_HOURS = 24


class SocAdminSite(AdminSite):
    site_header = "SOC_CENTRE"
    site_title = "INTEL"
    index_title = "Active OPS"

    def get_urls(self):
        urls = super().get_urls()
        siem = [path("siem/", self.admin_view(self.siem_view), name="siem")]
        return siem + urls

    def get_app_list(self, request, *args, **kwargs):
        app_list = super().get_app_list(request, *args, **kwargs)
        siem_url = reverse("soc_admin:siem")
        app_list.insert(0, {
            "name": "Security Operations",
            "app_label": "soc",
            "app_url": siem_url,
            "models": [
                {
                    "name": "SIEM overview",
                    "object_name": "SIEM",
                    "admin_url": siem_url,
                    "add_url": None,
                    "view_only": True,
                },
            ],
        })
        return app_list

    def siem_view(self, request):
        events = collect_events(hours=WINDOW_HOURS)
        alerts = detect(events, RULES, now=timezone.now())
        context = self.each_context(request)
        context.update({
            "title": "SIEM overview",
            "alerts": alerts,
            "rules": RULES,
            "events": events[:15],
            "window_hours": WINDOW_HOURS,
            "generated_at": timezone.now(),
            "stats": {
                "events": len(events),
                "alerts": len(alerts),
                "critical": sum(1 for alert in alerts if alert["severity"] >= 4),
                "failed_logins": sum(1 for event in events if event["event_type"] == "auth_failure"),
                "unique_ips": len({event["src_ip"] for event in events if event["src_ip"]}),
                "admin_changes": sum(1 for event in events if event["event_type"].startswith("admin_")),
            },
        })
        logger.info(
            "siem panel requested by=%s events=%s alerts=%s",
            request.user, len(events), len(alerts),
        )
        return TemplateResponse(request, "admin/siem.html", context)


soc_admin = SocAdminSite(name="soc_admin")


class ReadOnlyAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BulletinAdmin(admin.ModelAdmin):
    list_display = (
        "title", "writeup_category", "writeup_platform",
        "writeup_difficulty", "writeup_author", "publication_date",
    )
    list_filter = ("writeup_category", "writeup_platform", "writeup_difficulty")
    search_fields = ("title", "writeup_body", "writeup_author")
    date_hierarchy = "publication_date"
    prepopulated_fields = {"writeup_slug": ("title",)}
    readonly_fields = ("publication_date",)
    fieldsets = (
        (None, {"fields": ("title", "writeup_body", "writeup_image")}),
        ("Classification", {
            "description": "Categorize this bulletin for easier discovery.",
            "fields": (
                ("writeup_category", "writeup_platform"),
                ("writeup_difficulty", "writeup_author"),
            ),
        }),
        ("SEO & metadata", {
            "classes": ("collapse",),
            "fields": ("writeup_slug", "publication_date"),
        }),
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "created_on", "active")
    list_filter = ("active",)
    search_fields = ("body", "author", "post__title")
    date_hierarchy = "created_on"
    readonly_fields = ("created_on",)
    actions = ("approve_comments", "hide_comments")

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        updated = queryset.update(active=True)
        logger.info("comments approved count=%s by=%s", updated, request.user)
        self.message_user(request, f"{updated} comment(s) approved.", messages.SUCCESS)

    @admin.action(description="Hide selected comments")
    def hide_comments(self, request, queryset):
        updated = queryset.update(active=False)
        logger.warning("comments hidden count=%s by=%s", updated, request.user)
        self.message_user(request, f"{updated} comment(s) hidden.", messages.SUCCESS)


class TrainingOfferingAdmin(admin.ModelAdmin):
    list_display = (
        "title", "kind", "track", "level", "hours",
        "hourly_rate_kes", "is_active", "sort_order",
    )
    list_filter = ("kind", "track", "level", "is_active")
    list_editable = ("is_active", "sort_order")
    search_fields = ("title", "summary", "details")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "kind", "track", "level")}),
        ("Offer", {
            "fields": ("summary", "details", "hours", "hourly_rate_kes", "is_active", "sort_order"),
        }),
    )


class TrainingOfferAdmin(admin.ModelAdmin):
    list_display = ("callsign", "kind", "contact", "offering", "is_reviewed", "created_at")
    list_filter = ("kind", "is_reviewed")
    list_editable = ("is_reviewed",)
    list_select_related = ("offering",)
    search_fields = ("callsign", "contact", "message", "link")
    date_hierarchy = "created_at"
    readonly_fields = ("callsign", "contact", "kind", "link", "message", "offering", "created_at")
    actions = ("mark_reviewed", "mark_unreviewed")

    @admin.action(description="Mark selected offers reviewed")
    def mark_reviewed(self, request, queryset):
        updated = queryset.update(is_reviewed=True)
        logger.info("offers reviewed count=%s by=%s", updated, request.user)
        self.message_user(request, f"{updated} offer(s) marked reviewed.", messages.SUCCESS)

    @admin.action(description="Mark selected offers unreviewed")
    def mark_unreviewed(self, request, queryset):
        updated = queryset.update(is_reviewed=False)
        logger.warning("offers reopened count=%s by=%s", updated, request.user)
        self.message_user(request, f"{updated} offer(s) reopened.", messages.SUCCESS)


class LogEntryAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("action_time", "user", "content_type", "object_repr", "action_flag")
    list_filter = ("action_flag", "content_type", "user")
    search_fields = ("object_repr", "change_message")
    date_hierarchy = "action_time"


class SecurityEventAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("ts", "severity", "event_type", "source", "src_ip", "user", "target")
    list_filter = ("event_type", "source", "severity")
    search_fields = ("src_ip", "user", "target", "message")
    date_hierarchy = "ts"
    readonly_fields = ("ts", "source", "event_type", "src_ip", "user", "target", "message", "severity")
    actions = ("generate_demo",)

    @admin.action(description="Generate demo telemetry")
    def generate_demo(self, request, queryset):
        count = seed_demo_events()
        logger.info("demo telemetry seeded count=%s by=%s", count, request.user)
        self.message_user(request, f"{count} demo events ingested.", messages.SUCCESS)


for model, model_admin in (
    (Bulletins, BulletinAdmin),
    (Comment, CommentAdmin),
    (LogEntry, LogEntryAdmin),
    (SecurityEvent, SecurityEventAdmin),
    (TrainingOffering, TrainingOfferingAdmin),
    (TrainingOffer, TrainingOfferAdmin),
    (Site, SiteAdmin),
):
    soc_admin.register(model, model_admin)
