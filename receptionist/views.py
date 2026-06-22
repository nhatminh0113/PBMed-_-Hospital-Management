from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date, timedelta
from django.utils import timezone

from patients.models import Appointment, Status, PatientProfile, ExaminationRecord
from users.models import Doctors, Patients, Specialty, ReceptionistProfile

User = get_user_model()

STATUS_ACCEPTED = 'Accepted'
STATUS_WAITED = 'Waited'
STATUS_CANCELLED = 'Cancelled'


def receptionist_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_receptionist:
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required(login_url='/login')
@receptionist_required
def dashboard(request):
    today = date.today()
    apps_today = Appointment.objects.filter(start_date=today).select_related('patient_profile', 'doctor__user', 'status')

    return render(request, 'receptionist/dashboard.html', {
        'appointments_today': apps_today,
        'total_appointments_today': apps_today.count(),
        'accepted_today': apps_today.filter(status__status=STATUS_ACCEPTED).count(),
        'waited_today': apps_today.filter(status__status=STATUS_WAITED).count(),
        'cancelled_today': apps_today.filter(status__status=STATUS_CANCELLED).count(),
        'examined_today': ExaminationRecord.objects.filter(exam_date__date=today).count(),
        'doctors_available': Doctors.objects.select_related('user', 'specialty').all(),
        'today': today,
    })


@login_required(login_url='/login')
@receptionist_required
def appointments(request):
    if request.method == 'POST':
        app = get_object_or_404(Appointment, id=request.POST.get('app_id'))
        action = request.POST.get('action')

        if action == 'confirm':
            app.status = Status.objects.get(status=STATUS_ACCEPTED)
            app.confirmed_at = timezone.now()
            app.save()
            messages.success(request, f'Đã xác nhận lịch hẹn của {app.patient_profile.full_name}', extra_tags='success')
        elif action == 'cancel':
            app.status = Status.objects.get(status=STATUS_CANCELLED)
            app.rejected_at = timezone.now()
            app.rejection_reason = request.POST.get('reason', '')
            app.save()
            messages.success(request, f'Đã hủy lịch hẹn của {app.patient_profile.full_name}', extra_tags='success')
        return redirect('receptionist_appointments')

    fs = request.GET.get('filter_status', '')
    fd = request.GET.get('filter_date', '')
    fdoc = request.GET.get('filter_doctor', '')

    apps = Appointment.objects.select_related('patient_profile', 'doctor__user', 'status').order_by('-start_date', 'time')
    if fs:
        apps = apps.filter(status__status=fs)
    if fd:
        apps = apps.filter(start_date=fd)
    else:
        apps = apps.filter(start_date=date.today())
    if fdoc:
        apps = apps.filter(doctor__user__id=fdoc)

    return render(request, 'receptionist/appointments.html', {
        'appointments': apps,
        'doctors': Doctors.objects.select_related('user').all(),
        'statuses': Status.objects.all(),
        'filter_status': fs, 'filter_date': fd, 'filter_doctor': fdoc,
    })


@login_required(login_url='/login')
@receptionist_required
def walkin(request):
    doctors = Doctors.objects.select_related('user', 'specialty').all()
    times = [f'{h:02d}:{m:02d}' for h in range(8, 17) for m in [0, 30]]

    if request.method == 'POST':
        name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        birth_year = request.POST.get('birth_year', '').strip()
        doctor_id = request.POST.get('doctor_id')
        start_date = request.POST.get('start_date')
        time_str = request.POST.get('time')

        if not all([name, phone, birth_year, doctor_id, start_date, time_str]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
            return render(request, 'receptionist/walkin.html', {
                'doctors': doctors, 'times': times, 'form_data': request.POST,
            })

        username = f'bn_{phone}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': name.split()[-1] if len(name.split()) > 1 else name,
                'last_name': name.split()[0] if len(name.split()) > 1 else '',
                'email': f'{username}@pbmed.vn',
            }
        )
        if created:
            user.set_password('123456')
            user.save()
            Patients.objects.create(user=user)

        profile = PatientProfile.objects.filter(user=user, full_name=name).first()
        if not profile:
            profile = PatientProfile.objects.create(
                user=user, full_name=name,
                birth_year=int(birth_year) if birth_year.isdigit() else 1990,
                birth_date=request.POST.get('birth_date') or None,
                gender=request.POST.get('gender', 'Male'), phone=phone,
            )

        from patients.models import Time as TimeModel
        time_obj, _ = TimeModel.objects.get_or_create(time=time_str)
        Appointment.objects.create(
            doctor=get_object_or_404(Doctors, pk=doctor_id),
            patient=user.patients, patient_profile=profile,
            summary=request.POST.get('summary', 'Khám tại quầy'),
            description=f'Đăng ký tại quầy - {name}',
            start_date=start_date, time=time_obj,
            status=Status.objects.get(status=STATUS_WAITED),
        )

        messages.success(request, f'Đã đăng ký khám cho {name} lúc {time_str} ngày {start_date}', extra_tags='success')
        return redirect('receptionist_appointments')

    return render(request, 'receptionist/walkin.html', {'doctors': doctors, 'times': times})


@login_required(login_url='/login')
@receptionist_required
def patient_list(request):
    keyword = request.GET.get('keyword', '')
    profiles = PatientProfile.objects.select_related('user').all().order_by('-created_at')
    if keyword:
        profiles = profiles.filter(
            Q(full_name__icontains=keyword) | Q(phone__icontains=keyword) | Q(cccd__icontains=keyword)
        )
    return render(request, 'receptionist/patients.html', {'profiles': profiles, 'keyword': keyword})


@login_required(login_url='/login')
@receptionist_required
def schedule(request):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # Gộp query: đếm số lịch hẹn theo từng bác sĩ trong tuần
    from django.db.models import Count, Q as Q_
    stats = Doctors.objects.annotate(
        total=Count('appointment', filter=Q_(appointment__start_date__gte=week_start, appointment__start_date__lte=week_end)),
        accepted=Count('appointment', filter=Q_(appointment__status__status=STATUS_ACCEPTED, appointment__start_date__gte=week_start, appointment__start_date__lte=week_end)),
        waited=Count('appointment', filter=Q_(appointment__status__status=STATUS_WAITED, appointment__start_date__gte=week_start, appointment__start_date__lte=week_end)),
        today_count=Count('appointment', filter=Q_(appointment__start_date=today)),
    ).select_related('user', 'specialty')

    weekdays = [week_start + timedelta(days=i) for i in range(7)]

    return render(request, 'receptionist/schedule.html', {
        'doctor_stats': stats,
        'weekdays': weekdays,
        'week_start': week_start, 'week_end': week_end, 'today': today,
        'appointments_today': Appointment.objects.filter(start_date=today).select_related(
            'patient_profile', 'doctor__user', 'status'
        ).order_by('time'),
    })


@login_required(login_url='/login')
@receptionist_required
def profile(request):
    p, _ = ReceptionistProfile.objects.get_or_create(user=request.user)
    return render(request, 'receptionist/profile.html', {'profile': p})

