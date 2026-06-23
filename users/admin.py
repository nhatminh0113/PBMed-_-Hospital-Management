from django.contrib import admin
from .models import Users, Doctors, Patients, Specialty, ReceptionistProfile, Reste_token

admin.site.register(Users)
admin.site.register(Doctors)
admin.site.register(Patients)
admin.site.register(Specialty)
admin.site.register(ReceptionistProfile)
admin.site.register(Reste_token)
