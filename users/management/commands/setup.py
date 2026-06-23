from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Thiết lập database: migrate + seed data (ORM)'

    def handle(self, *args, **options):
        self.stdout.write('1/3 Đang migrate...')
        call_command('migrate', verbosity=0)

        self.stdout.write('2/3 Đang tạo dữ liệu mẫu...')
        self._seed_specialties()
        self._seed_users()
        self._seed_profiles()
        self._seed_catalogs()
        self._seed_appointments()

        self.stdout.write(self.style.SUCCESS('\n3/3 Hoàn tất!'))
        self.stdout.write(self.style.SUCCESS('\nTài khoản mẫu:'))
        self.stdout.write('  Admin:        admin / 123456')
        self.stdout.write('  Bác sĩ:       doc001-doc005 / 123456')
        self.stdout.write('  Lễ tân:       reception01-reception02 / 123456')
        self.stdout.write('  Bệnh nhân:    patient01-patient05 / 123456')

    def _seed_specialties(self):
        from users.models import Specialty
        if Specialty.objects.exists():
            self.stdout.write('  -> Chuyên khoa đã có, bỏ qua.')
            return
        names = [
            'Nội tổng quát', 'Tim mạch', 'Da liễu', 'Cơ xương khớp',
            'Tiêu hóa', 'Thần kinh', 'Mắt', 'Nhi khoa', 'Tâm thần', 'Miễn dịch',
        ]
        for name in names:
            Specialty.objects.create(name=name, description=name)
        self.stdout.write(f'  -> {len(names)} chuyên khoa')

    def _seed_users(self):
        from users.models import Doctors, Patients, ReceptionistProfile
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('  -> Người dùng đã có, bỏ qua.')
            return

        # Admin
        admin = User.objects.create_superuser(
            username='admin', password='123456', email='admin@pbmed.vn',
            first_name='Quan tri', last_name='He thong',
        )
        admin.is_admin = True
        admin.save()

        # Doctors - realistic names
        doc_data = [
            ('doc001', 'Tuấn', 'Nguyễn Văn', 1),
            ('doc002', 'Hương', 'Lê Thị', 2),
            ('doc003', 'Mạnh', 'Phạm Đức', 3),
            ('doc004', 'Lan', 'Đỗ Thị', 4),
            ('doc005', 'Quang', 'Hoàng Minh', 5),
        ]
        from users.models import Specialty
        for username, fn, ln, spec_id in doc_data:
            u = User.objects.create_user(
                username=username, password='123456',
                email=f'{username}@pbmed.vn',
                first_name=fn, last_name=ln, is_doctor=True,
            )
            Doctors.objects.create(
                user=u, specialty=Specialty.objects.get(id=spec_id),
                bio=f'Bác sĩ chuyên khoa {Specialty.objects.get(id=spec_id).name}',
            )
        self.stdout.write(f'  -> {len(doc_data)} bác sĩ')

        # Receptionists
        for username in ['reception01', 'reception02']:
            u = User.objects.create_user(
                username=username, password='123456',
                email=f'{username}@pbmed.vn',
                first_name='Lễ tân', last_name=username,
                is_receptionist=True,
            )
            ReceptionistProfile.objects.create(user=u, employee_id=username)
        self.stdout.write('  -> 2 lễ tân')

        # Patients - realistic Vietnamese names
        from patients.models import PatientProfile
        patient_data = [
            ('patient01', 'Nguyễn Văn An', 1985, 'Male', '0901234501', 'BHYT-VN001', '12 Nguyễn Trãi, Thanh Xuân', 'Hà Nội'),
            ('patient02', 'Trần Thị Bình', 1992, 'Female', '0901234502', 'BHYT-VN002', '45 Láng Hạ, Đống Đa', 'Hà Nội'),
            ('patient03', 'Lê Văn Cường', 1978, 'Male', '0901234503', 'BHYT-VN003', '78 Giải Phóng, Hai Bà Trưng', 'Hà Nội'),
            ('patient04', 'Phạm Thị Dung', 1995, 'Female', '0901234504', 'BHYT-VN004', '23 Tây Sơn, Đống Đa', 'Hà Nội'),
            ('patient05', 'Hoàng Văn Em', 1988, 'Male', '0901234505', 'BHYT-VN005', '56 Kim Mã, Ba Đình', 'Hà Nội'),
        ]
        for username, full_name, birth_year, gender, phone, insurance, address, city in patient_data:
            names = full_name.split()
            last_name = names[0]
            first_name = ' '.join(names[1:]) if len(names) > 1 else full_name
            u = User.objects.create_user(
                username=username, password='123456',
                email=f'{username}@pbmed.vn',
                first_name=first_name, last_name=last_name,
            )
            Patients.objects.create(user=u)
            PatientProfile.objects.create(
                user=u, full_name=full_name,
                birth_year=birth_year, birth_date=date(birth_year, 6, 15),
                gender=gender, phone=phone, insurance=insurance,
                address=address, city=city,
            )
        self.stdout.write('  -> 5 bệnh nhân')

    def _seed_profiles(self):
        from users.models import ReceptionistProfile
        ReceptionistProfile.objects.update_or_create(
            user=User.objects.get(username='reception01'),
            defaults={'employee_id': 'REC001', 'start_date': date(2025, 1, 1)},
        )
        ReceptionistProfile.objects.update_or_create(
            user=User.objects.get(username='reception02'),
            defaults={'employee_id': 'REC002', 'start_date': date(2025, 6, 1)},
        )

    def _seed_catalogs(self):
        from patients.models import Status, Time, CLSService
        if Status.objects.exists():
            return
        Status.objects.create(id=1, status='Accepted')
        Status.objects.create(id=2, status='Waited')
        Status.objects.create(id=3, status='Cancelled')
        Status.objects.create(id=4, status='Da kham')
        self.stdout.write('  -> 4 trạng thái')

        if not Time.objects.exists():
            for t in ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
                      '11:00', '13:00', '13:30', '14:00', '14:30', '15:00',
                      '15:30', '16:00']:
                Time.objects.create(time=t)
            self.stdout.write(f'  -> {Time.objects.count()} khung giờ')

        if not CLSService.objects.exists():
            cls_list = [
                'Xét nghiệm máu', 'Xét nghiệm nước tiểu', 'Siêu âm tổng quát',
                'X-quang ngực', 'Điện tâm đồ', 'Sinh hóa máu', 'Nội soi tiêu hóa',
            ]
            for name in cls_list:
                CLSService.objects.create(name=name, description=name)
            self.stdout.write(f'  -> {len(cls_list)} dịch vụ CLS')

    def _seed_appointments(self):
        from patients.models import Appointment, PatientProfile, Status, Time, ExaminationRecord, CLSIndication, CLSService
        from users.models import Doctors, Patients
        if Appointment.objects.exists():
            self.stdout.write('  -> Lich hen da co, bo qua.')
            return

        status_w = Status.objects.get(status='Waited')
        status_a = Status.objects.get(status='Accepted')
        status_c = Status.objects.get(status='Cancelled')
        status_dk = Status.objects.get(status='Da kham')
        today = date.today()

        doc1 = Doctors.objects.get(user__username='doc001')
        doc2 = Doctors.objects.get(user__username='doc002')
        doc3 = Doctors.objects.get(user__username='doc003')
        doc4 = Doctors.objects.get(user__username='doc004')
        doc5 = Doctors.objects.get(user__username='doc005')
        pats = [Patients.objects.get(user__username=f'patient0{i}') for i in range(1, 6)]
        pps = [PatientProfile.objects.filter(user__username=f'patient0{i}').first() for i in range(1, 6)]
        times = list(Time.objects.all().order_by('id'))

        def t(idx):
            return times[idx % len(times)]

        # Create 12 appointments across different doctors/patients/statuses
        apps_data = [
            # (doctor, patient, profile, summary, days_from_today, time_idx, status, confirmed, rejected_reason)
            (doc1, pats[0], pps[0], 'Đau bụng, buồn nôn', 1, 2, status_w, False, ''),
            (doc1, pats[1], pps[1], 'Khám tim mạch định kỳ', 0, 4, status_a, True, ''),
            (doc2, pats[2], pps[2], 'Đau lưng, mỏi mệt', 2, 1, status_c, False, 'Bệnh nhân bận'),
            (doc2, pats[0], pps[0], 'Tái khám dạ dày', -1, 3, status_dk, True, ''),
            (doc3, pats[3], pps[3], 'Phát ban, ngứa', 1, 5, status_w, False, ''),
            (doc3, pats[1], pps[1], 'Khám da liễu định kỳ', 0, 6, status_a, True, ''),
            (doc4, pats[4], pps[4], 'Đau cơ xương khớp', 3, 0, status_w, False, ''),
            (doc4, pats[2], pps[2], 'Khám cơ xương khớp', -2, 7, status_dk, True, ''),
            (doc5, pats[3], pps[3], 'Rối loạn tiêu hóa', 1, 8, status_a, True, ''),
            (doc5, pats[4], pps[4], 'Đau dạ dày, ợ chua', -3, 9, status_dk, True, ''),
            (doc1, pats[2], pps[2], 'Sốt, ho, khác dị ứng', 2, 10, status_w, False, ''),
            (doc2, pats[3], pps[3], 'Đau ngực, khó thở', 0, 11, status_a, True, ''),
        ]

        apps = []
        for doctor, patient, profile, summary, days, tidx, status, confirmed, reason in apps_data:
            start = today + timedelta(days=days)
            a = Appointment.objects.create(
                doctor=doctor, patient=patient, patient_profile=profile,
                summary=summary, start_date=start, time=t(tidx), status=status,
                confirmed_at=timezone.now() if confirmed else None,
                rejection_reason=reason if reason else '',
            )
            apps.append(a)
        self.stdout.write(f'  -> {len(apps)} lịch hẹn')

        # Create examination records for appointments that were seen (status = Da kham or Accepted with past date)
        cls_services = list(CLSService.objects.all())
        exams_created = 0
        cls_created = 0

        for i, a in enumerate(apps):
            if a.status.status in ('Da kham', 'Accepted') and a.start_date <= today:
                from datetime import datetime
                exam_date = datetime.combine(a.start_date, datetime.min.time()).replace(hour=9 + (i % 8))
                exam_date = timezone.make_aware(exam_date) if timezone.is_naive(exam_date) else exam_date
                if exam_date > timezone.now():
                    exam_date = timezone.now() - timedelta(hours=2)

                record = ExaminationRecord.objects.create(
                    patient_profile=a.patient_profile,
                    doctor=a.doctor,
                    appointment=a,
                    exam_date=exam_date,
                    room=f'Phòng {300 + (i % 10)}',
                    reason=a.summary,
                    diagnosis=[
                        'Viêm dạ dày cấp nghi do HP - chỉ định nội soi kiểm tra',
                        'Tăng huyết áp giai đoạn 2 - nguy cơ tim mạch cao',
                        'Viêm phế quản cấp - nghi nhiễm khuẩn hô hấp',
                        'Rối loạn tiền đình - chưa loại trừ thiểu năng tuần hoàn não',
                        'Đau thắt lưng do thoái hóa cột sống - điều trị nội khoa',
                        'Viêm amidan cấp do liên cầu khuẩn - cần kháng sinh',
                        'Đái tháo đường type 2 - đường huyết chưa kiểm soát',
                        'Thiếu máu cơ tim nhẹ - cần theo dõi và điều chỉnh thuốc',
                        'Viêm xoang mạn tính - tái khám sau 2 tuần',
                        'Suy nhược thần kinh - rối loạn lo âu',
                        'Viêm loét dạ dày tá tràng - tiến triển tốt sau điều trị',
                        'Rối loạn mỡ máu - nguy cơ tim mạch trung bình',
                    ][i % 12],
                    pulse=f'{60 + (i * 5) % 40}',
                    temperature=f'{36 + (i % 10) / 10:.1f}',
                    blood_pressure=f'{110 + (i * 3) % 30}/{70 + (i * 2) % 20}',
                    weight=f'{55 + (i * 7) % 25}',
                    health_status=f'Bệnh nhân tỉnh, tiếp xúc tốt. {["Sinh tồn ổn định, đáp ứng tốt điều trị", "cần theo dõi thêm 1 tuần", "đã cải thiện rõ rệt, giảm các triệu chứng", "chuyển biến tốt, xuất viện được"][i % 4]}',
                    medical_history=f'Tiền sử: {["Không có gì đặc biệt", "Tăng huyết áp 3 năm", "Đã từng phẫu thuật ruột thừa 2019", "Viêm loét dạ dày 2 năm", "Hen phế quản từ nhỏ"][i % 5]}',
                    family_history=f'Gia đình: {["Không có bệnh lý đặc biệt", "Bố bị tim mạch, mẹ bị tiểu đường", "Mẹ bị tăng huyết áp", "Anh trai bị viêm gan B", "Bố mất vì tai biến mạch não"][i % 5]}',
                )
                exams_created += 1

                # Add CLS indications
                num_cls = (i % 3) + 1  # 1-3 CLS per exam
                for j in range(num_cls):
                    svc = cls_services[(i * 3 + j) % len(cls_services)]
                    result = f'Kết quả {svc.name}: Bình thường, không phát hiện bất thường' if (i + j) % 2 == 0 else f'Kết quả {svc.name}: Có biểu hiện bất thường, cần theo dõi thêm'
                    CLSIndication.objects.create(
                        examination_record=record,
                        cls_service=svc,
                        status='completed' if (i + j) % 2 == 0 else 'pending',
                        result=result if (i + j) % 2 == 0 else '',
                        result_date=timezone.now() if (i + j) % 2 == 0 else None,
                        performed_by=a.doctor.user if (i + j) % 2 == 0 else None,
                    )
                    cls_created += 1

        self.stdout.write(f'  -> {exams_created} phiếu khám')
        self.stdout.write(f'  -> {cls_created} chỉ định CLS')

        # Update completed appointments status to Da kham
        Appointment.objects.filter(
            id__in=[a.id for a in apps if a.status.status == 'Accepted' and a.start_date <= today]
        ).update(status=Status.objects.get(status='Da kham'))
        self.stdout.write('  -> Cập nhật trạng thái "Đã khám" cho các lịch đã khám')

        # ====== DEMO CHI TIẾT CHO BÁC SĨ NGUYỄN VĂN TUẤN (doc001) ======
        self.stdout.write('\n  == CHI TIẾT DEMO BÁC SĨ NGUYỄN VĂN TUẤN ==')
        doc1_apps = Appointment.objects.filter(doctor=doc1).order_by('start_date')
        self.stdout.write(f'  -> {doc1_apps.count()} lịch hẹn cho doc001')

        # Ensure doc001 has at least 8 appointments across all statuses
        doc1_patients_cycle = [pats[i % 5] for i in range(8)]
        doc1_profiles_cycle = [pps[i % 5] for i in range(8)]
        doc1_statuses = [status_w, status_a, status_dk, status_c, status_w, status_a, status_dk, status_w]
        doc1_summaries = [
            'Đau bụng thắt lưng, buồn nôn, sốt 37.5 độ',
            'Khám tim mạch định kỳ - Huyết áp cao 160/90',
            'Tái khám dạ dày - đã uống thuốc 2 tuần',
            'Đau họng, ho, sốt 38 độ - nghi viêm amidan',
            'Khám tổng quát - định kỳ 6 tháng',
            'Đau tức hạ sườn phải, sau ăn nhiều mỡ',
            'Khám lại - thuốc hạ huyết áp có tác dụng phụ',
            'Đầy bụng, ợ chua, đại tiện lỏng nhiều ngày',
        ]
        doc1_confirmed = [False, True, True, False, False, True, True, False]

        doc1_apps_count = doc1_apps.count()
        for i in range(max(0, 8 - doc1_apps_count)):
            idx = doc1_apps_count + i
            Appointment.objects.get_or_create(
                doctor=doc1, patient=doc1_patients_cycle[idx], patient_profile=doc1_profiles_cycle[idx],
                summary=doc1_summaries[idx], start_date=today + timedelta(days=idx - 10),
                time=times[idx % len(times)], status=doc1_statuses[idx],
                defaults={
                    'confirmed_at': timezone.now() if doc1_confirmed[idx] else None,
                    'description': f'Chi tiết: {doc1_summaries[idx]}',
                }
            )
        self.stdout.write(f'  -> Doc001 có {Appointment.objects.filter(doctor=doc1).count()} lịch hẹn')

        # Create 6 detailed examination records for doc001
        doc1_exam_apps = Appointment.objects.filter(
            doctor=doc1, status__status__in=['Da kham', 'Accepted']
        ).filter(start_date__lte=today)[:6]

        doc1_exam_data = [
            {
                'room': 'Phòng 301',
                'reason': 'Đau bụng vùng thượng vị, buồn nôn, sốt nhẹ 37.5 độ',
                'vitals': {'pulse': '78', 'temperature': '37.5', 'blood_pressure': '120/80', 'weight': '65'},
                'health': 'Bệnh nhân tỉnh, tiếp xúc tốt. Bụng mềm, ấn đau vùng thượng vị. Không có phản ứng thành bụng.',
                'diagnosis': 'Viêm dạ dày cấp do HP (nhiễm khuẩn)',
                'history': 'Tiền sử viêm dạ dày từ 2022, đã điều trị nhiều đợt. Hút thuốc lá 10 năm, uống rượu bia thường xuyên.',
                'family': 'Gia đình: Bố bị viêm loét dạ dày, Mẹ bị tăng huyết áp.',
                'cls': [
                    ('Xét nghiệm máu', 'completed', 'HC: 14.2 g/dL, BC: 12.5K (tăng), CRP: 25 mg/L (tăng), glucose: 95 mg/dL (bình thường)'),
                    ('Xét nghiệm nước tiểu', 'completed', 'Màu sắc: vàng nhạt, Tỷ trọng: 1015, Protein: (-), Glucose: (-), Hồng cầu: 0-1, Bạch cầu: 1-2'),
                    ('Siêu âm tổng quát', 'pending', ''),
                ]
            },
            {
                'room': 'Phòng 302',
                'reason': 'Khám tim mạch định kỳ - HA cao 160/90, đau đầu, hoa mắt',
                'vitals': {'pulse': '82', 'temperature': '36.8', 'blood_pressure': '160/95', 'weight': '68'},
                'health': 'Bệnh nhân tỉnh, thể trạng trung bình. Tim đều, T1 T2 rõ. Phổi không ran. HA cao 160/95mmHg.',
                'diagnosis': 'Tăng huyết áp giai đoạn 2 - Nguy cơ tim mạch cao',
                'history': 'Tăng HA từ 2021, đã điều trị bằng Amlodipin 5mg. Không thường xuyên tái khám.',
                'family': 'Gia đình: Bố bị tăng HA + tai biến mạch não năm 2020.',
                'cls': [
                    ('Điện tâm đồ', 'completed', 'ECG: Nhịp xoang 78/p. Trục sóng bình thường. ST chênh nhẹ ở V5-V6. Không có QT kéo dài. Kết luận: Thiếu máu cơ tim nhẹ.'),
                    ('Xét nghiệm máu', 'completed', 'Mỡ máu: LDL 3.8 mmol/L (tăng), Triglycerid 2.5 mmol/L (tăng). HDL 1.2 mmol/L (bình thường). Glucose 5.6 mmol/L (bình thường).'),
                    ('Sinh hóa máu', 'pending', ''),
                ]
            },
            {
                'room': 'Phòng 303',
                'reason': 'Tái khám dạ dày - đã uống thuốc 2 tuần, còn đau ít',
                'vitals': {'pulse': '75', 'temperature': '37.0', 'blood_pressure': '130/85', 'weight': '66'},
                'health': 'Sau 2 tuần điều trị, tình trạng cải thiện. Bụng mềm, không còn đau nhiều. Ăn uống tốt hơn.',
                'diagnosis': 'Viêm dạ dày - đáp ứng tốt với điều trị. Tiếp tục thuốc thêm 2 tuần.',
                'history': 'Viêm dạ dày mạn tính. Đã điều trị bằng Amoxicillin + Clarithromycin + Omeprazole.',
                'family': 'Gia đình: Không có gì đặc biệt.',
                'cls': [
                    ('Siêu âm tổng quát', 'completed', 'Siêu âm: Dạ dày bình thường, không thấy dị vật hay ổ loét. Gan, túi mật, tụy, lách bình thường.'),
                ]
            },
            {
                'room': 'Phòng 304',
                'reason': 'Đau họng, ho, sốt 38 độ - nghi viêm amidan',
                'vitals': {'pulse': '88', 'temperature': '38.2', 'blood_pressure': '125/80', 'weight': '64'},
                'health': 'Bệnh nhân sốt, họng sưng đỏ, amidan 2 bên to đỏ, có xuất tiết mũi sau. HA bình thường.',
                'diagnosis': 'Viêm amidan cấp do liên cầu khuẩn',
                'history': 'Không có tiền sử đặc biệt. Lần đầu bị viêm amidan nặng.',
                'family': 'Gia đình: Chị gái bị viêm amidan mạn tính.',
                'cls': [
                    ('Xét nghiệm máu', 'completed', 'BC: 14.2K (tăng cao), CRP: 45 mg/L (tăng). NEU: Trung tính tăng. Soi: Không thấy ký sinh trùng.'),
                    ('Sinh hóa máu', 'pending', ''),
                ]
            },
            {
                'room': 'Phòng 305',
                'reason': 'Khám tổng quát định kỳ 6 tháng',
                'vitals': {'pulse': '70', 'temperature': '36.5', 'blood_pressure': '115/75', 'weight': '67'},
                'health': 'Bệnh nhân khỏe, không có biểu hiện bệnh lý. Thể trạng tốt, cân nặng ổn định.',
                'diagnosis': 'Sức khỏe tốt - không phát hiện bệnh lý. Khuyến nghị tập thể dục đều, ăn uống điều độ.',
                'history': 'Tiền sử khỏe. Không hút thuốc, uống rượu bia ít.',
                'family': 'Gia đình: Mẹ bị tiểu đường type 2. Cần kiểm tra đường huyết định kỳ.',
                'cls': [
                    ('Xét nghiệm máu', 'completed', 'HC: 15.0 g/dL, BC: 7.2K (bình thường), Tiểu cầu: 250K. Glucose: 92 mg/dL (bình thường).'),
                    ('Xét nghiệm nước tiểu', 'completed', 'Màu: vàng đậm, Tỷ trọng: 1020, Protein: (-), Glucose: (-), Aceton: (-).'),
                    ('Sinh hóa máu', 'completed', 'AST: 25 U/L, ALT: 30 U/L, Creatinin: 0.9 mg/dL, Ure: 25 mg/dL. Cholesterol: 190 mg/dL.'),
                ]
            },
            {
                'room': 'Phòng 306',
                'reason': 'Đau tức hạ sườn phải, sau ăn nhiều mỡ, buồn nôn',
                'vitals': {'pulse': '80', 'temperature': '36.9', 'blood_pressure': '145/90', 'weight': '66'},
                'health': 'Bệnh nhân đau tức vùng hạ sườn phải, lan ra sau lưng. Murphy (+) nhẹ. Ăn mỡ thấy đau tăng.',
                'diagnosis': 'Viêm túi mật cấp do sỏi mật',
                'history': 'Tiền sử viêm túi mật nhẹ 2023. Ăn nhiều mỡ, ít rau xanh.',
                'family': 'Gia đình: Chị bị sỏi mật đã mổ. Mẹ bị tăng huyết áp.',
                'cls': [
                    ('Siêu âm tổng quát', 'completed', 'Siêu âm: Gan bình thường, túi mật dày nhẹ (4mm), có 1 sỏi 8mm trong lòng túi mật. Dưới mật không giãn.'),
                    ('Xét nghiệm máu', 'completed', 'BC: 10.5K (tăng nhẹ), CRP: 30 mg/L. Bilirubin: 1.2 mg/dL (bình thường). AST/ALT: 35/42 (bình thường).'),
                    ('Sinh hóa máu', 'pending', ''),
                ]
            },
        ]

        cls_svc_map = {s.name: s for s in CLSService.objects.all()}
        performed_by = User.objects.get(username='doc001')
        exams_created = 0
        cls_created = 0

        for i, a in enumerate(doc1_exam_apps):
            from datetime import datetime
            if ExaminationRecord.objects.filter(appointment=a).exists():
                continue
            edate = datetime.combine(a.start_date, datetime.min.time()).replace(hour=8 + i)
            edate = timezone.make_aware(edate) if timezone.is_naive(edate) else edate

            data = doc1_exam_data[i % len(doc1_exam_data)]
            record = ExaminationRecord.objects.create(
                patient_profile=a.patient_profile,
                doctor=doc1, appointment=a, exam_date=edate,
                room=data['room'],
                reason=data['reason'],
                diagnosis=data['diagnosis'],
                pulse=data['vitals']['pulse'],
                temperature=data['vitals']['temperature'],
                blood_pressure=data['vitals']['blood_pressure'],
                weight=data['vitals']['weight'],
                health_status=data['health'],
                medical_history=data['history'],
                family_history=data['family'],
            )
            exams_created += 1

            for cls_name, cls_status, cls_result in data['cls']:
                svc = cls_svc_map.get(cls_name)
                if not svc:
                    continue
                CLSIndication.objects.create(
                    examination_record=record, cls_service=svc,
                    status=cls_status,
                    result=cls_result if cls_status == 'completed' else '',
                    result_date=timezone.now() if cls_status == 'completed' else None,
                    performed_by=performed_by if cls_status == 'completed' else None,
                )
                cls_created += 1

        self.stdout.write(f'  -> Doc001: {exams_created} phiếu khám tiếng Việt')
        self.stdout.write(f'  -> Doc001: {cls_created} chỉ định CLS tiếng Việt')
