from django.contrib import admin
from .models import Bulletins, Comment
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.sites.models import Site



class SocAdminSite(AdminSite):
    site_header="SOC_CENTRE"
    site_title="INTEL"
    index_title="Active OPS"
#Instantiation has to happen below its model bcs the compiler has no idea what soc_admin is...
soc_admin=SocAdminSite(name='soc_admin')


@admin.register(Bulletins, site=soc_admin)
class BulletinAdmin(admin.ModelAdmin):


    list_display = ('title', 'writeup_category', 'writeup_platform', 'writeup_difficulty', 'writeup_author')
    list_filter = ('writeup_category', 'writeup_platform', 'writeup_difficulty') # Added for better UX

    # Prepopulated fields make the "SEO thingie" (the slug) happen automatically!
    prepopulated_fields = {'writeup_slug': ('title',)}

    fieldsets = (
        (None, {  # None means no header for the first section
            'fields': ('title', 'writeup_body')
        }),
        ('Classification', {
            'description': "Categorize this bulletin for easier discovery.",
            'fields': (
                ('writeup_category', 'writeup_platform'), # Putting them in a tuple makes them appear side-by-side!
                ('writeup_difficulty', 'writeup_author'),
            ),
        }),
        ('SEO & URL Settings', {
            'classes': ('collapse',),
            'fields': ('writeup_slug',),
        }),
    )

@admin.register(LogEntry, site=soc_admin)
class LogentryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ('action_flag', 'content_type', 'user')
    search_fields = ('object_repr', 'change_message')

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return True
    def has_delete_permission(self, request, obj=None): return True

@admin.register(Comment, site=soc_admin)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('body', 'author', 'post')

from django.contrib.sites.admin import SiteAdmin
soc_admin.register(Site, SiteAdmin)

    #No need for JWT cs Django's default is safer + out_of-box CSRF protection.