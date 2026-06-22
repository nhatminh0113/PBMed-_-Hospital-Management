from django.urls import path
from .views import (
    patient_dashboard, book_appointment, my_appointments, patient_confirm_book,
    profile_list, profile_create, profile_edit, profile_delete,
    exam_history, cls_results
)
from doctors.views import profile

urlpatterns = [
  path('patient_dashboard/', patient_dashboard, name='patient_dashboard'),
  path('profile/', profile, name='patient_profile'),
  
  path('book_appointment/', book_appointment, name='book_appointment'),
  path('my_appointments/', my_appointments, name='my_appointments'),
  path('patient_confirm_book/<str:doctor>/', patient_confirm_book, name='patient_confirm_book'),
  
  # Hồ sơ bệnh nhân
  path('profiles/', profile_list, name='profile_list'),
  path('profiles/create/', profile_create, name='profile_create'),
  path('profiles/<int:profile_id>/edit/', profile_edit, name='profile_edit'),
  path('profiles/<int:profile_id>/delete/', profile_delete, name='profile_delete'),
  
  # Lịch sử khám & CLS
  path('profiles/<int:profile_id>/history/', exam_history, name='exam_history'),
  path('profiles/<int:profile_id>/cls-results/', cls_results, name='cls_results'),
]
