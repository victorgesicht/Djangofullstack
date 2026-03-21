


from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.urls import path, include
#do and create the migrations{TASK 0000234}
from api.admin import soc_admin
from api.sitemaps import StaticViewSitemap

# We put our sitemaps in a dictionary
sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    #idea to have the admin/ for an auto-ban script
    path('tee/', admin.site.urls),
    #path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('soc_admin/',soc_admin.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]


#learn reverse