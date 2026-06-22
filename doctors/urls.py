from django.urls import path
from .views import (
    doctor_dashboard, profile, view_appointments,
    doctor_patient_list,
    doctor_exam_list, doctor_exam_create, doctor_exam_detail,
    doctor_exam_edit, doctor_add_cls,
    cls_pending_list, cls_update_result
)

urlpatterns = [
  path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
  path('profile/', profile, name='doctor_profile'),
  
  # Danh sách bệnh nhân
  path('doctor_patient_list/', doctor_patient_list, name='doctor_patient_list'),
  
  # Quản lý lịch hẹn
  path('view_appointments/', view_appointments, name='view_appointments'),
  
  # Khám bệnh
  path('doctor_exam_list/', doctor_exam_list, name='doctor_exam_list'),
  path('doctor_exam_create/<int:appointment_id>/', doctor_exam_create, name='doctor_exam_create'),
  path('doctor_exam_detail/<int:exam_id>/', doctor_exam_detail, name='doctor_exam_detail'),
  path('doctor_exam_edit/<int:exam_id>/', doctor_exam_edit, name='doctor_exam_edit'),
  path('doctor_add_cls/<int:exam_id>/', doctor_add_cls, name='doctor_add_cls'),
  
  # Cận lâm sàng
  path('cls_pending/', cls_pending_list, name='cls_pending_list'),
  path('cls_update/<int:indication_id>/', cls_update_result, name='cls_update_result'),
]
