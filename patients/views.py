from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date, timedelta

from patients.models import Appointment, Time, Status, PatientProfile, ExaminationRecord, CLSIndication
from users.models import Doctors, Specialty, Patients


@login_required(login_url='/login')
def patient_dashboard(request):
    return redirect('book_appointment')


@login_required(login_url='/login')
def my_appointments(request):
    apps = Appointment.objects.filter(patient__user=request.user).select_related(
        'doctor__user', 'status', 'time', 'patient_profile'
    )
    fs = request.GET.get('filter_status')
    fd = request.GET.get('filter_date')
    fn = request.GET.get('filter_doctor_name')

    if fs and fs != 'All':
        apps = apps.filter(status__status=fs)
    if fd:
        apps = apps.filter(start_date=fd)
    if fn:
        apps = apps.filter(doctor__user__first_name__icontains=fn)

    return render(request, 'patients/my_appointments.html', {
        'appointments': apps,
        'filter_status': fs, 'filter_date': fd, 'filter_doctor_name': fn,
    })


@login_required(login_url='/login')
def book_appointment(request):
    doctors = Doctors.objects.select_related('user', 'specialty').all()
    times = Time.objects.all()
    specialities = Specialty.objects.all()
    
    fs = request.GET.get('filter_speciality')
    fn = request.GET.get('filter_doctor_name')
    if fs and fs != 'All':
        doctors = doctors.filter(specialty__name=fs)
    if fn:
        doctors = doctors.filter(user__first_name__icontains=fn)

    today = date.today()
    weekday_names = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN']
    next_days = [
        {'date': today + timedelta(days=i), 'day_num': (today + timedelta(days=i)).day,
         'month_num': (today + timedelta(days=i)).month,
         'weekday': weekday_names[(today + timedelta(days=i)).weekday()],
         'date_str': (today + timedelta(days=i)).strftime('%Y-%m-%d')}
        for i in range(7)
    ]

    morning = [t for t in times if int(t.time.split(':')[0]) < 12]
    afternoon = [t for t in times if int(t.time.split(':')[0]) >= 12]

    return render(request, 'patients/book_appointment.html', {
        'doctors': doctors, 'times': times, 'specialities': specialities,
        'morning_slots': morning, 'afternoon_slots': afternoon,
        'next_days': next_days, 'today': today,
        'filter_speciality': fs, 'filter_doctor_name': fn,
    })


@login_required(login_url='/login')
def patient_confirm_book(request, doctor):
    doc = get_object_or_404(Doctors, user__username=doctor)

    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        if not profile_id:
            messages.error(request, 'Vui lòng chọn hồ sơ bệnh nhân.')
            return redirect('book_appointment')
        profile = get_object_or_404(PatientProfile, id=profile_id, user=request.user)
        time_obj = get_object_or_404(Time, time=request.POST.get('time'))

        Appointment.objects.create(
            summary=request.POST.get('summary', ''),
            description=request.POST.get('description', ''),
            start_date=request.POST.get('date'),
            time=time_obj,
            doctor=doc,
            patient=get_object_or_404(Patients, user=request.user),
            status=Status.objects.get(status='Waited'),
            patient_profile=profile,
        )
        return render(request, 'patients/patient_confirm_book.html', {
            'doctor': doc, 'times': Time.objects.all(),
            'profiles': PatientProfile.objects.filter(user=request.user),
            'preselect_date': request.POST.get('date'),
            'preselect_time': request.POST.get('time'),
            'booking_success': True,
        })

    return render(request, 'patients/patient_confirm_book.html', {
        'times': Time.objects.all(), 'doctor': doc,
        'profiles': PatientProfile.objects.filter(user=request.user),
        'preselect_date': request.GET.get('date', ''),
        'preselect_time': request.GET.get('time', ''),
    })


# ====== HỒ SƠ BỆNH NHÂN ======

@login_required(login_url='/login')
def profile_list(request):
    return render(request, 'patients/profile_list.html', {
        'profiles': PatientProfile.objects.filter(user=request.user),
    })


@login_required(login_url='/login')
def profile_create(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        birth_date = request.POST.get('birth_date', '').strip()
        if not full_name or not birth_date:
            messages.error(request, 'Vui lòng nhập họ tên và ngày sinh.')
        else:
            bd = request.POST.get('birth_date')
            PatientProfile.objects.create(
                user=request.user, full_name=full_name,
                birth_year=int(bd[:4]) if bd else 2000,
                birth_date=bd or None,
                gender=request.POST.get('gender', 'Male'),
                phone=request.POST.get('phone', ''), cccd=request.POST.get('cccd', ''),
                address=request.POST.get('address', ''), ward=request.POST.get('ward', ''),
                city=request.POST.get('city', ''), insurance=request.POST.get('insurance', ''),
            )
            messages.success(request, 'Tạo hồ sơ thành công!', extra_tags='success')
            return redirect('profile_list')
    return render(request, 'patients/profile_form.html', {'action': 'Tạo'})


@login_required(login_url='/login')
def profile_edit(request, profile_id):
    profile = get_object_or_404(PatientProfile, id=profile_id, user=request.user)
    if request.method == 'POST':
        for field in ['full_name', 'phone', 'cccd', 'address', 'ward', 'city', 'insurance']:
            setattr(profile, field, request.POST.get(field, ''))
        bd = request.POST.get('birth_date')
        profile.birth_year = int(bd[:4]) if bd else 2000
        profile.birth_date = bd or None
        profile.gender = request.POST.get('gender', 'Male')
        profile.save()
        messages.success(request, 'Cập nhật hồ sơ thành công!', extra_tags='success')
        return redirect('profile_list')
    return render(request, 'patients/profile_form.html', {'profile': profile, 'action': 'Sửa'})


@login_required(login_url='/login')
def profile_delete(request, profile_id):
    profile = get_object_or_404(PatientProfile, id=profile_id, user=request.user)
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Đã xoá hồ sơ.', extra_tags='success')
    return redirect('profile_list')


# ====== LỊCH SỬ KHÁM & CLS ======

@login_required(login_url='/login')
def exam_history(request, profile_id):
    profile = get_object_or_404(PatientProfile, id=profile_id, user=request.user)
    return render(request, 'patients/exam_history.html', {
        'profile': profile,
        'records': ExaminationRecord.objects.filter(patient_profile=profile).select_related(
            'doctor__user', 'doctor__specialty'
        ),
    })


@login_required(login_url='/login')
def cls_results(request, profile_id):
    profile = get_object_or_404(PatientProfile, id=profile_id, user=request.user)
    return render(request, 'patients/cls_results.html', {
        'profile': profile,
        'indications': CLSIndication.objects.filter(
            examination_record__patient_profile=profile
        ).select_related('cls_service', 'examination_record__doctor__user'),
    })
