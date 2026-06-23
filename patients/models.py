from django.db import models
from users.models import Patients, Doctors, Users


class Time(models.Model):
    time = models.CharField(max_length=10)

    class Meta:
        db_table = 'time_slot'
        verbose_name = 'Giờ'
        verbose_name_plural = 'Giờ'

    def __str__(self):
        return self.time


class Status(models.Model):
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'appointment_status'
        verbose_name = 'Trạng thái'
        verbose_name_plural = 'Trạng thái'

    def __str__(self):
        return self.status


class PatientProfile(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='patient_profiles')
    full_name = models.CharField(max_length=100)
    birth_year = models.IntegerField()
    birth_date = models.DateField(null=True, blank=True, verbose_name='Ngày sinh')
    gender = models.CharField(max_length=10, choices=(('Male', 'Nam'), ('Female', 'Nữ')), default='Male')
    phone = models.CharField(max_length=15, blank=True, default='')
    cccd = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    ward = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    insurance = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'patient_profile'
        verbose_name = 'Hồ sơ bệnh nhân'
        verbose_name_plural = 'Hồ sơ bệnh nhân'

    def __str__(self):
        return f'{self.full_name} ({self.user.username})'


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    patient_profile = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField()
    description = models.TextField(blank=True, default='')
    start_date = models.DateField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, default=1)
    rejection_reason = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'appointment'
        verbose_name = 'Lịch hẹn'
        verbose_name_plural = 'Lịch hẹn'

    def __str__(self):
        return self.summary


class CLSService(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'cls_service'
        verbose_name = 'Dịch vụ CLS'
        verbose_name_plural = 'Dịch vụ CLS'

    def __str__(self):
        return self.name


class ExaminationRecord(models.Model):
    patient_profile = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='exam_records')
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, related_name='exam_records')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    exam_date = models.DateTimeField(auto_now_add=True)
    room = models.CharField(max_length=50, blank=True, default='')
    reason = models.TextField(blank=True, default='')
    medical_history = models.TextField(blank=True, default='')
    family_history = models.TextField(blank=True, default='')
    pulse = models.CharField(max_length=20, blank=True, default='')
    temperature = models.CharField(max_length=20, blank=True, default='')
    blood_pressure = models.CharField(max_length=20, blank=True, default='')
    weight = models.CharField(max_length=20, blank=True, default='')
    health_status = models.TextField(blank=True, default='')
    diagnosis = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'examination_record'
        verbose_name = 'Phiếu khám'
        verbose_name_plural = 'Phiếu khám'
        ordering = ['-exam_date']

    def __str__(self):
        return f'PK {self.id} - {self.patient_profile.full_name} ({self.exam_date.strftime("%d/%m/%Y")})'


class CLSIndication(models.Model):
    examination_record = models.ForeignKey(ExaminationRecord, on_delete=models.CASCADE, related_name='cls_indications')
    cls_service = models.ForeignKey(CLSService, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('pending', 'Chờ kết quả'), ('completed', 'Đã có kết quả')), default='pending')
    result = models.TextField(blank=True, default='')
    result_date = models.DateTimeField(null=True, blank=True)
    performed_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'cls_indication'
        verbose_name = 'Chỉ định CLS'
        verbose_name_plural = 'Chỉ định CLS'

    def __str__(self):
        return f'{self.cls_service.name} - {self.examination_record.patient_profile.full_name}'
