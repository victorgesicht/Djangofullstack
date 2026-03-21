
from django.urls import path
from .views import Index,BulletingDetailView, IntelDetailView, IntelNotes, Lboard
from django.views.generic.base import TemplateView


urlpatterns = [
    path('', Index.as_view(), name='index'),
    #path('api/var/log', BulletinsListView.as_view(), name='bulletins'),
    path('bulletin/<uuid:pk>/',BulletingDetailView.as_view(), name='bulletin'),
    path('intel/<uuid:pk>/',IntelDetailView.as_view(), name='intel'),
    path('ID/',IntelNotes.as_view(), name='id'),
    path('L-board', Lboard.as_view(),name='LBoard'),
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    #path('extract-cv/', Extract-cv.as_view(), name='extract-cv')

]