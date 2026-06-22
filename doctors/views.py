from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date, timedelta
from django.utils import timezone

from patients.models import Appointment, Status, ExaminationRecord, CLSIndication
from users.models import Doctors, Specialty

STATUS_ACCEPTED = 'Accepted'
STATUS_WAITED = 'Waited'
STATUS_CANCELLED = 'Cancelled'


@login_required(login_url='/login')
def doctor_dashboard(request):
    doctor = request.user.doctors
    today = date.today()
    month_start = today.replace(day=1)

    # Stats
    examined_today = ExaminationRecord.objects.filter(doctor=doctor, exam_date__date=today).count()
    appointments_today = Appointment.objects.filter(doctor=doctor, start_date=today).count()
    examined_week = ExaminationRecord.objects.filter(doctor=doctor, exam_date__date__gte=today - timedelta(days=7)).count()
    examined_month = ExaminationRecord.objects.filter(doctor=doctor, exam_date__date__gte=month_start).count()
    cls_month = CLSIndication.objects.filter(
        examination_record__doctor=doctor, examination_record__exam_date__date__gte=month_start
    ).count()
    total_examined = ExaminationRecord.objects.filter(doctor=doctor).count()
    total_cls = CLSIndication.objects.filter(examination_record__doctor=doctor).count()
    total_pending_cls = CLSIndication.objects.filter(examination_record__doctor=doctor, status='pending').count()

    # Activity feed - gộp 4 query thành 1 list rồi sort
    activities = []

    for app in Appointment.objects.filter(doctor=doctor, status__status=STATUS_ACCEPTED
        ).exclude(confirmed_at__isnull=True).select_related('patient_profile').order_by('-confirmed_at')[:5]:
        activities.append(('confirm', app.confirmed_at, f'Xác nhận lịch hẹn cho {app.patient_profile.full_name}',
                          app.start_date.strftime('%d/%m/%Y') if app.start_date else ''))

    for app in Appointment.objects.filter(doctor=doctor, status__status=STATUS_CANCELLED
        ).exclude(rejected_at__isnull=True).select_related('patient_profile').order_by('-rejected_at')[:5]:
        activities.append(('cancel', app.rejected_at, f'Hủy lịch hẹn của {app.patient_profile.full_name}',
                          app.start_date.strftime('%d/%m/%Y') if app.start_date else ''))

    for exam in ExaminationRecord.objects.filter(doctor=doctor
        ).select_related('patient_profile').order_by('-exam_date')[:5]:
        activities.append(('exam', exam.exam_date, f'Khám bệnh cho {exam.patient_profile.full_name}',
                          f'Phòng {exam.room}' if exam.room else ''))

    for cls in CLSIndication.objects.filter(examination_record__doctor=doctor, status='completed'
        ).exclude(result_date__isnull=True).select_related('cls_service', 'examination_record__patient_profile'
        ).order_by('-result_date')[:5]:
        activities.append(('cls', cls.result_date, f'Kết quả {cls.cls_service.name} cho {cls.examination_record.patient_profile.full_name}', ''))

    activities.sort(key=lambda x: x[1] or timezone.now(), reverse=True)
    activities = activities[:10]

    return render(request, 'doctors/doctor_dashboard.html', {
        'examined_today': examined_today,
        'appointments_today': appointments_today,
        'examined_week': examined_week,
        'examined_month': examined_month,
        'cls_month': cls_month,
        'total_examined': total_examined,
        'total_pending_cls': total_pending_cls,
        'activities': activities,
        'today': today,
    })


@login_required(login_url='/login')
def view_appointments(request):
    if request.method == 'POST':
        app = get_object_or_404(Appointment, id=request.POST.get('app'))
        new_status = request.POST.get('status')
        app.status = get_object_or_404(Status, status=new_status)
        if new_status == STATUS_ACCEPTED:
            app.confirmed_at = timezone.now()
        elif new_status == STATUS_CANCELLED:
            app.rejected_at = timezone.now()
        app.save()

    apps = Appointment.objects.filter(doctor__user=request.user).select_related('patient_profile', 'status')
    fs = request.GET.get('filter_status')
    fd = request.GET.get('filter_date')
    fn = request.GET.get('filter_patient_name')

    if fs and fs != 'All':
        apps = apps.filter(status__status=fs)
    if fd:
        apps = apps.filter(start_date=fd)
    if fn:
        apps = apps.filter(patient_profile__full_name__icontains=fn)

    return render(request, 'doctors/viewappointments.html', {
        'appointments': apps,
        'filter_status': fs, 'filter_date': fd, 'filter_patient_name': fn,
    })


@login_required(login_url='/login')
def doctor_patient_list(request):
    doctor = request.user.doctors
    records = ExaminationRecord.objects.filter(doctor=doctor).select_related(
        'patient_profile', 'appointment'
    ).order_by('-exam_date')

    keyword = request.GET.get('keyword', '')
    if keyword:
        records = records.filter(
            Q(patient_profile__full_name__icontains=keyword) |
            Q(patient_profile__phone__icontains=keyword) |
            Q(patient_profile__cccd__icontains=keyword)
        )

    filter_status = request.GET.get('filter_status', 'all')
    if filter_status == 'pending_cls':
        records = records.filter(cls_indications__status='pending').distinct()

    today = date.today()
    patient_data = [{
        'record': r,
        'age': today.year - r.patient_profile.birth_year,
        'pending_cls': r.cls_indications.filter(status='pending').count(),
    } for r in records]

    return render(request, 'doctors/patient_list.html', {
        'patient_data': patient_data, 'keyword': keyword, 'filter_status': filter_status,
    })


@login_required(login_url='/login')
def doctor_exam_list(request):
    doctor = request.user.doctors
    apps = Appointment.objects.filter(doctor=doctor, status__status=STATUS_ACCEPTED).select_related('patient_profile')
    examined_ids = set(ExaminationRecord.objects.filter(doctor=doctor).values_list('appointment_id', flat=True))

    return render(request, 'doctors/exam_list.html', {
        'not_examined': apps.exclude(id__in=examined_ids),
        'examined': apps.filter(id__in=examined_ids),
    })


@login_required(login_url='/login')
def doctor_exam_create(request, appointment_id):
    doctor = request.user.doctors
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    existing = ExaminationRecord.objects.filter(appointment=appointment, doctor=doctor).first()
    if existing:
        return redirect('doctor_exam_detail', exam_id=existing.id)

    if request.method == 'POST':
        if not appointment.patient_profile:
            messages.error(request, 'Lịch hẹn này chưa có hồ sơ bệnh nhân.')
            return redirect('doctor_exam_list')

        record = ExaminationRecord.objects.create(
            patient_profile=appointment.patient_profile, doctor=doctor, appointment=appointment,
            room=request.POST.get('room', ''), reason=request.POST.get('reason', ''),
            medical_history=request.POST.get('medical_history', ''),
            family_history=request.POST.get('family_history', ''),
            pulse=request.POST.get('pulse', ''), temperature=request.POST.get('temperature', ''),
            blood_pressure=request.POST.get('blood_pressure', ''),
            weight=request.POST.get('weight', ''),
            health_status=request.POST.get('health_status', ''),
            diagnosis=request.POST.get('diagnosis', ''),
        )

        for cls_id in request.POST.getlist('cls_services'):
            if cls_id:
                from patients.models import CLSService, CLSIndication
                CLSIndication.objects.create(
                    examination_record=record,
                    cls_service=get_object_or_404(CLSService, id=int(cls_id)),
                )

        if appointment.status.status != STATUS_ACCEPTED:
            appointment.status = Status.objects.get(status=STATUS_ACCEPTED)
            appointment.confirmed_at = timezone.now()
            appointment.save()

        messages.success(request, 'Tạo phiếu khám thành công!', extra_tags='success')
        return redirect('doctor_exam_detail', exam_id=record.id)

    from patients.models import CLSService
    return render(request, 'doctors/exam_form.html', {
        'appointment': appointment,
        'profile': appointment.patient_profile,
        'cls_services': CLSService.objects.all(),
    })


@login_required(login_url='/login')
def doctor_exam_detail(request, exam_id):
    record = get_object_or_404(
        ExaminationRecord.objects.select_related(
            'patient_profile', 'doctor__user', 'appointment'
        ).prefetch_related('cls_indications__cls_service'),
        id=exam_id, doctor=request.user.doctors,
    )
    return render(request, 'doctors/exam_detail.html', {'record': record})


@login_required(login_url='/login')
def doctor_exam_edit(request, exam_id):
    record = get_object_or_404(ExaminationRecord, id=exam_id, doctor=request.user.doctors)
    if request.method == 'POST':
        for field in ['room', 'reason', 'medical_history', 'family_history',
                       'pulse', 'temperature', 'blood_pressure', 'weight',
                       'health_status', 'diagnosis']:
            setattr(record, field, request.POST.get(field, ''))
        record.save()
        messages.success(request, 'Cập nhật phiếu khám thành công!', extra_tags='success')
        return redirect('doctor_exam_detail', exam_id=record.id)

    from patients.models import CLSService
    return render(request, 'doctors/exam_edit.html', {
        'record': record, 'cls_services': CLSService.objects.all(),
    })


@login_required(login_url='/login')
def doctor_add_cls(request, exam_id):
    record = get_object_or_404(ExaminationRecord, id=exam_id, doctor=request.user.doctors)
    if request.method == 'POST':
        from patients.models import CLSService, CLSIndication
        added = 0
        for cls_id in request.POST.getlist('cls_services'):
            if cls_id:
                _, created = CLSIndication.objects.get_or_create(
                    examination_record=record,
                    cls_service=get_object_or_404(CLSService, id=int(cls_id)),
                )
                if created:
                    added += 1
        if added:
            messages.success(request, f'Đã thêm {added} chỉ định CLS!', extra_tags='success')
        else:
            messages.error(request, 'Các chỉ định đã tồn tại.')
        return redirect('doctor_exam_detail', exam_id=record.id)

    from patients.models import CLSService
    existing_ids = record.cls_indications.values_list('cls_service_id', flat=True)
    return render(request, 'doctors/add_cls.html', {
        'record': record, 'cls_services': CLSService.objects.all(),
        'existing_ids': list(existing_ids),
    })


@login_required(login_url='/login')
def cls_pending_list(request):
    from patients.models import CLSIndication
    return render(request, 'doctors/cls_pending.html', {
        'indications': CLSIndication.objects.filter(status='pending').select_related(
            'cls_service', 'examination_record__patient_profile', 'examination_record__doctor__user'
        ).order_by('examination_record__exam_date'),
    })


@login_required(login_url='/login')
def cls_update_result(request, indication_id):
    from patients.models import CLSIndication
    indication = get_object_or_404(CLSIndication, id=indication_id, status='pending')
    if request.method == 'POST':
        indication.result = request.POST.get('result', '')
        indication.status = 'completed'
        indication.result_date = timezone.now()
        indication.performed_by = request.user
        indication.save()
        messages.success(request, f'Đã cập nhật kết quả cho {indication.cls_service.name}!', extra_tags='success')
        return redirect('cls_pending_list')
    return render(request, 'doctors/cls_result_form.html', {'indication': indication})


@login_required(login_url='/login')
def profile(request):
    """Profile chung cho cả doctor và patient — chỉnh sửa thông tin cá nhân"""
    specialities = Specialty.objects.all()
    updated_profile = False
    updated_password = False

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            u = request.user
            u.first_name = request.POST.get('user_firstname', '')
            u.last_name = request.POST.get('user_lastname', '')
            u.gender = request.POST.get('user_gender', 'Male')
            u.birthday = request.POST.get('birthday') or None
            u.save()

            if u.is_doctor:
                doc = u.doctors
                spec_name = request.POST.get('Speciality')
                if spec_name:
                    doc.specialty = get_object_or_404(Specialty, name=spec_name)
                doc.save()
            updated_profile = True

        elif 'update_password' in request.POST:
            if not request.user.check_password(request.POST.get('current_password', '')):
                messages.error(request, 'Mật khẩu hiện tại không đúng.')
            elif request.POST.get('new_password') != request.POST.get('confirm_new_password'):
                messages.error(request, 'Mật khẩu mới không khớp.')
            elif len(request.POST.get('new_password', '')) < 6:
                messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự.')
            else:
                request.user.set_password(request.POST.get('new_password'))
                request.user.save()
                update_session_auth_hash(request, request.user)
                updated_password = True

    return render(request, 'doctors/profile.html', {
        'basicdata': request.user,
        'specialities': specialities,
        'updated_profile_successfully': updated_profile,
        'updated_password_successfully': updated_password,
        'base_template': 'doctors/base.html' if request.user.is_doctor else 'patients/base.html',
    })
