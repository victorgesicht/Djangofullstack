
from django.urls import path
from .views import Index, BulletinsListView, BulletingDetailView, IntelDetailView, IntelNotes

urlpatterns = [
    path('', Index.as_view(), name='index'),
    #path('api/var/log', BulletinsListView.as_view(), name='bulletins'),
    path('bulletin/<uuid:pk>/',BulletingDetailView.as_view(), name='bulletin'),
    path('intel/<uuid:pk>/',IntelDetailView.as_view(), name='intel'),
    path('intel',IntelNotes.as_view(), name='notes'),

]