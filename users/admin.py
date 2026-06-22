from django.contrib import admin
from .models import Users, Address, Doctors, Patients, Specialty, ReceptionistProfile

admin.site.register(Address)
admin.site.register(Users)
admin.site.register(Doctors)
admin.site.register(Patients)
admin.site.register(Specialty)
admin.site.register(ReceptionistProfile)
