from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date, timedelta
from django.http import HttpResponse
import csv

from patients.models import Appointment, PatientProfile, ExaminationRecord, CLSIndication
from users.models import Doctors, Patients, Specialty, ReceptionistProfile

User = get_user_model()


def admin_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped


def csv_export(filename, headers, rows):
    """Helper xuất CSV với BOM cho Excel"""
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    resp.write('\ufeff')
    w = csv.writer(resp)
    w.writerow(headers)
    for row in rows:
        w.writerow(row)
    return resp


# ====== DASHBOARD ======

@login_required(login_url='/login')
@admin_required
def dashboard(request):
    today = date.today()
    ms = today.replace(day=1)

    return render(request, 'administration/dashboard.html', {
        'total_doctors': Doctors.objects.count(),
        'total_patients': Patients.objects.count(),
        'total_receptionists': User.objects.filter(is_receptionist=True).count(),
        'total_appointments': Appointment.objects.count(),
        'total_examined': ExaminationRecord.objects.count(),
        'total_cls': CLSIndication.objects.count(),
        'total_pending_cls': CLSIndication.objects.filter(status='pending').count(),
        'app_month': Appointment.objects.filter(start_date__gte=ms).count(),
        'exam_month': ExaminationRecord.objects.filter(exam_date__date__gte=ms).count(),
        'cls_month': CLSIndication.objects.filter(examination_record__exam_date__date__gte=ms).count(),
        'app_today': Appointment.objects.filter(start_date=today).count(),
        'exam_today': ExaminationRecord.objects.filter(exam_date__date=today).count(),
        'top_doctors': Doctors.objects.annotate(
            total_exams=Count('exam_records')
        ).select_related('user', 'specialty').order_by('-total_exams')[:5],
        'specialty_stats': Specialty.objects.annotate(
            doctor_count=Count('doctors'), exam_count=Count('doctors__exam_records')
        ).order_by('-exam_count'),
        'today': today,
    })


# ====== QUẢN LÝ TÀI KHOẢN ======


def _get_users(role_filter='', keyword=''):
    """Lấy danh sách users theo role"""
    if role_filter == 'doctor':
        qs = User.objects.filter(is_doctor=True).select_related('doctors__specialty')
    elif role_filter == 'receptionist':
        qs = User.objects.filter(is_receptionist=True)
    elif role_filter == 'patient':
        qs = User.objects.filter(patients__isnull=False)
    else:
        qs = User.objects.all().select_related('doctors__specialty')

    if keyword:
        qs = qs.filter(Q(username__icontains=keyword) | Q(first_name__icontains=keyword)
                       | Q(last_name__icontains=keyword) | Q(email__icontains=keyword))
    return qs.order_by('-date_joined')[:100]


def _handle_receptionist_profile(user, data):
    """Tạo/cập nhật hồ sơ lễ tân"""
    p, _ = ReceptionistProfile.objects.get_or_create(user=user)
    for f in ['phone', 'address', 'employee_id', 'note']:
        setattr(p, f, data.get(f, ''))
    p.start_date = data.get('start_date') or None
    p.save()


@login_required(login_url='/login')
@admin_required
def user_management(request):
    return render(request, 'administration/users.html', {
        'users': _get_users(request.GET.get('role', ''), request.GET.get('keyword', '')),
        'role_filter': request.GET.get('role', ''),
        'keyword': request.GET.get('keyword', ''),
    })


@login_required(login_url='/login')
@admin_required
def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, 'Tên đăng nhập và mật khẩu là bắt buộc.')
            return render(request, 'administration/user_form.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            return render(request, 'administration/user_form.html')

        user = User.objects.create_user(username=username, password=password,
            first_name=request.POST.get('first_name', '').strip(),
            last_name=request.POST.get('last_name', '').strip(),
            email=request.POST.get('email', '').strip() or f'{username}@pbmed.vn')

        role = request.POST.get('role', 'patient')
        if role == 'doctor':
            user.is_doctor = True
            user.save()
            sid = request.POST.get('specialty')
            if sid:
                Doctors.objects.create(user=user, specialty=get_object_or_404(Specialty, pk=sid))
        elif role == 'receptionist':
            user.is_receptionist = True
            user.save()
            _handle_receptionist_profile(user, request.POST)
        else:
            Patients.objects.create(user=user)

        messages.success(request, f'Đã tạo tài khoản {username}', extra_tags='success')
        return redirect('admin_users')

    return render(request, 'administration/user_form.html', {
        'specialties': Specialty.objects.all(), 'edit_mode': False,
    })


@login_required(login_url='/login')
@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        for f in ['first_name', 'last_name', 'email']:
            setattr(user, f, request.POST.get(f, '').strip())
        user.save()

        pwd = request.POST.get('password', '').strip()
        if pwd:
            user.set_password(pwd)
            user.save()

        new_role = request.POST.get('role', '')
        if new_role == 'doctor' and not user.is_doctor:
            user.is_doctor, user.is_receptionist = True, False
            user.save()
            sid = request.POST.get('specialty')
            if sid:
                Doctors.objects.get_or_create(user=user, defaults={'specialty': get_object_or_404(Specialty, pk=sid)})
        elif new_role == 'receptionist' and not user.is_receptionist:
            user.is_receptionist, user.is_doctor = True, False
            user.save()
            ReceptionistProfile.objects.get_or_create(user=user)
        elif new_role == 'patient':
            user.is_doctor = user.is_receptionist = False
            user.save()
            Patients.objects.get_or_create(user=user)

        if user.is_receptionist:
            _handle_receptionist_profile(user, request.POST)

        messages.success(request, f'Đã cập nhật tài khoản {user.username}', extra_tags='success')
        return redirect('admin_users')

    rp = ReceptionistProfile.objects.filter(user=user).first() if user.is_receptionist else None
    return render(request, 'administration/user_form.html', {
        'edit_user': user, 'specialties': Specialty.objects.all(),
        'edit_mode': True, 'receptionist_profile': rp,
    })


@login_required(login_url='/login')
@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'Đã xóa tài khoản', extra_tags='success')
    return redirect('admin_users')


# ====== QUẢN LÝ DANH MỤC ======

from patients.models import Status, CLSService


def _get_category_model(cat_type):
    if cat_type == 'specialty':
        return Specialty
    if cat_type == 'cls':
        return CLSService
    return None


@login_required(login_url='/login')
@admin_required
def category_management(request):
    return render(request, 'administration/categories.html', {
        'specialties': Specialty.objects.all().order_by('name'),
        'cls_services': CLSService.objects.all().order_by('name'),
        'statuses': Status.objects.all(),
    })


@login_required(login_url='/login')
@admin_required
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Tên danh mục là bắt buộc.')
            return redirect('admin_categories')

        cat_type = request.POST.get('type')
        if cat_type == 'specialty':
            Specialty.objects.create(name=name, description=request.POST.get('description', '').strip())
        elif cat_type == 'cls':
            CLSService.objects.create(name=name, description=request.POST.get('description', '').strip())
        elif cat_type == 'status':
            Status.objects.create(status=name)
        messages.success(request, f'Đã thêm {name}', extra_tags='success')
    return redirect('admin_categories')


@login_required(login_url='/login')
@admin_required
def category_edit(request, cat_type, cat_id):
    Model = _get_category_model(cat_type)
    if not Model:
        messages.error(request, 'Loại danh mục không hợp lệ.')
        return redirect('admin_categories')

    obj = get_object_or_404(Model, pk=cat_id)
    if request.method == 'POST':
        obj.name = request.POST.get('name', obj.name).strip()
        if hasattr(obj, 'description'):
            obj.description = request.POST.get('description', '').strip()
        obj.save()
        messages.success(request, f'Đã cập nhật {obj.name}', extra_tags='success')
        return redirect('admin_categories')

    return render(request, 'administration/category_edit.html', {'obj': obj, 'cat_type': cat_type})


@login_required(login_url='/login')
@admin_required
def category_delete(request, cat_type, cat_id):
    Model = _get_category_model(cat_type)
    if Model and request.method == 'POST':
        get_object_or_404(Model, pk=cat_id).delete()
        messages.success(request, 'Đã xóa', extra_tags='success')
    return redirect('admin_categories')


# ====== BÁO CÁO THỐNG KÊ ======

@login_required(login_url='/login')
@admin_required
def reports(request):
    today = date.today()
    months_data = []
    for i in range(11, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        start = date(y, m, 1)
        end = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
        months_data.append({
            'label': f'{m}/{y}',
            'apps': Appointment.objects.filter(start_date__gte=start, start_date__lt=end).count(),
            'exams': ExaminationRecord.objects.filter(exam_date__date__gte=start, exam_date__date__lt=end).count(),
        })

    return render(request, 'administration/reports.html', {
        'months_data': months_data,
        'status_counts': Appointment.objects.values('status__status').annotate(count=Count('id')),
        'specialty_exams': Specialty.objects.annotate(
            doctor_count=Count('doctors', distinct=True), exam_count=Count('doctors__exam_records', distinct=True),
            cls_count=Count('doctors__exam_records__cls_indications', distinct=True),
        ).order_by('-exam_count'),
        'cls_service_stats': CLSService.objects.annotate(
            total=Count('clsindication'),
            completed=Count('clsindication', filter=Q(clsindication__status='completed')),
            pending=Count('clsindication', filter=Q(clsindication__status='pending')),
        ).order_by('-total'),
        'today': today,
    })


@login_required(login_url='/login')
@admin_required
def report_export(request, report_type):
    if report_type == 'appointments':
        return csv_export('lich_hen',
            ['STT', 'Bệnh nhân', 'Bác sĩ', 'Ngày', 'Giờ', 'Trạng thái'],
            [[i, a.patient_profile.full_name or '', f'{a.doctor.user.last_name} {a.doctor.user.first_name}' if a.doctor else '',
              a.start_date, a.time.time if a.time else '', a.status.status if a.status else '']
             for i, a in enumerate(Appointment.objects.select_related('patient_profile', 'doctor__user', 'status').all(), 1)])

    if report_type == 'patients':
        return csv_export('benh_nhan',
            ['STT', 'Họ tên', 'Năm sinh', 'Giới tính', 'SĐT', 'CCCD', 'BHYT', 'Ngày tạo'],
            [[i, p.full_name, p.birth_year, 'Nam' if p.gender == 'Male' else 'Nữ',
              p.phone, p.cccd, p.insurance, p.created_at.strftime('%d/%m/%Y') if p.created_at else '']
             for i, p in enumerate(PatientProfile.objects.all(), 1)])

    if report_type == 'examinations':
        qs = ExaminationRecord.objects.select_related(
            'patient_profile', 'doctor__user', 'doctor__specialty').prefetch_related('cls_indications')
        return csv_export('phieu_kham',
            ['STT', 'Bệnh nhân', 'Bác sĩ', 'Khoa', 'Ngày khám', 'Chuẩn đoán', 'Số CLS'],
            [[i, r.patient_profile.full_name or '',
              f'{r.doctor.user.last_name} {r.doctor.user.first_name}' if r.doctor else '',
              r.doctor.specialty.name if r.doctor and hasattr(r.doctor, 'specialty') else '',
              r.exam_date.strftime('%d/%m/%Y') if r.exam_date else '', r.diagnosis,
              r.cls_indications.count()]
             for i, r in enumerate(qs, 1)])

    messages.error(request, 'Loại báo cáo không hợp lệ.')
    return redirect('admin_reports')
