from django.urls import path
from .views import (
    dashboard, appointments, walkin,
    patient_list, schedule, profile,
)

urlpatterns = [
    path('receptionist/', dashboard, name='receptionist_dashboard'),
    path('receptionist/profile/', profile, name='receptionist_profile'),
    path('receptionist/appointments/', appointments, name='receptionist_appointments'),
    path('receptionist/walkin/', walkin, name='receptionist_walkin'),
    path('receptionist/patients/', patient_list, name='receptionist_patients'),
    path('receptionist/schedule/', schedule, name='receptionist_schedule'),
]
