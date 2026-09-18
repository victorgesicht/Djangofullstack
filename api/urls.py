from django.urls import path
from .views import Index, Writeups, WriteUpDetailView, IntelDetailView, IntelNotes, Lboard
from django.views.generic.base import TemplateView


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('writeups/', Writeups.as_view(), name='writeups'),
    path('writeup/<uuid:pk>/', WriteUpDetailView.as_view(), name='writedetail'),
    path('intel/<uuid:pk>/', IntelDetailView.as_view(), name='intel'),
    path('ID/', IntelNotes.as_view(), name='id'),
    path('L-board', Lboard.as_view(), name='LBoard'),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]