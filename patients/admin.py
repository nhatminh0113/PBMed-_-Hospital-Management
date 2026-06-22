from django.contrib import admin
from .models import Status, Time, Appointment, PatientProfile, CLSService, ExaminationRecord, CLSIndication

admin.site.register(Status)
admin.site.register(Time)
admin.site.register(Appointment)

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'birth_year', 'gender', 'phone']

@admin.register(CLSService)
class CLSServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(ExaminationRecord)
class ExaminationRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_profile', 'doctor', 'exam_date', 'diagnosis']

@admin.register(CLSIndication)
class CLSIndicationAdmin(admin.ModelAdmin):
    list_display = ['cls_service', 'examination_record', 'status']
