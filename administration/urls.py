from django.urls import path
from .views import (
    dashboard, user_management, user_create, user_edit, user_delete,
    category_management, category_create, category_edit, category_delete,
    reports, report_export,
)

urlpatterns = [
    path('administration/', dashboard, name='admin_dashboard'),
    path('administration/users/', user_management, name='admin_users'),
    path('administration/users/create/', user_create, name='admin_user_create'),
    path('administration/users/<int:user_id>/edit/', user_edit, name='admin_user_edit'),
    path('administration/users/<int:user_id>/delete/', user_delete, name='admin_user_delete'),
    path('administration/categories/', category_management, name='admin_categories'),
    path('administration/categories/create/', category_create, name='admin_category_create'),
    path('administration/categories/<str:cat_type>/<int:cat_id>/edit/', category_edit, name='admin_category_edit'),
    path('administration/categories/<str:cat_type>/<int:cat_id>/delete/', category_delete, name='admin_category_delete'),
    path('administration/reports/', reports, name='admin_reports'),
    path('administration/reports/export/<str:report_type>/', report_export, name='admin_report_export'),
]
