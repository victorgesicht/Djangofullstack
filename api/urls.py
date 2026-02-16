
from django.urls import path
from .views import Index, BulletinsListView, BulletingDetailView

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('api/var/log', BulletinsListView.as_view(), name='bulletins'),
    path('bulletin_detail/<int:pk>/',BulletingDetailView.as_view, name='bulletin'),
]