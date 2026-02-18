from django.contrib import admin
from .models import Bulletins
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry


class SocAdminSite(AdminSite):
    site_header="SOC_CENTRE"
    site_title="INTEL"
    index_title="Active OPS"
#Instantiation has to happen below its model bcs the compiler has no idea what soc_admin is...
soc_admin=SocAdminSite(name='soc_admin')


@admin.register(Bulletins, site=soc_admin)
class BulletinAdmin(admin.ModelAdmin):
    list_display=('writeup_category', 'writeup_slug', 'writeup_platform', 'writeup_difficulty', 'writeup_body', 'title', 'writeup_author')
    search_fields=('writeup_category', 'writeup_slug', 'writeup_platform', 'writeup_difficulty', 'writeup_body', 'title', 'writeup_author')

@admin.register(LogEntry, site=soc_admin)
class LogentryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ('action_flag', 'content_type', 'user')
    search_fields = ('object_repr', 'change_message')

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False


    #No need for JWT cs Django's default is safer + out_of-box CSRF protection.