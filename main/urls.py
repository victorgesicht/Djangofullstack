



from django.contrib import admin
from django.urls import path, include
#do and create the migrations{TASK 0000234}
from api.admin import soc_admin

urlpatterns = [
    #idea to have the admin/ for an auto-ban script
    path('tee/', admin.site.urls),
    #path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('soc_admin/',soc_admin.urls),
]


#learn reverse