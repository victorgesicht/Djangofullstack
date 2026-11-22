from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from api.admin import soc_admin
from api.sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("tee/", admin.site.urls),
    path("", include("api.urls")),
    path("soc_admin/", soc_admin.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("martor/", include("martor.urls")),
]
