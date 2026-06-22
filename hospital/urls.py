from django.contrib import admin
from django.urls import path ,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('doctors.urls')),
    path('', include('patients.urls')),
    path('', include('receptionist.urls')),
    path('', include('administration.urls')),
]
