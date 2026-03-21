from django.contrib import sitemaps
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        # The names MUST match the 'name=' in your urls.py
        return ['index', 'id','LBoard']

    def location(self, item):
        return reverse(item)