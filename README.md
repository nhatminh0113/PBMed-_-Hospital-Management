# PBMed - Hệ thống Quản lý Bệnh viện

**Đồ án I** — Hoàng Minh Nhất (20237468)

PBMed là hệ thống quản lý bệnh viện xây dựng trên Django, hỗ trợ 4 vai trò: **Bệnh nhân**, **Bác sĩ**, **Lễ tân**, **Quản trị viên**.

---

## Công nghệ

| Thành phần | Công nghệ |
|-----------|-----------|
| Backend | Django 5.2 (Python 3.11) |
| Database | MySQL 8+ / 9.x |
| Frontend | Bootstrap 5, HTML templates |
| CSS/JS | Bootstrap Icons, Bootstrap Bundle |

---

## Cài đặt

### 1. Clone & vào thư mục

```bash
git clone <repo-url>
cd Hospital-Management-main
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv
source venv/Scripts/activate   # Git Bash
# hoặc: venv\Scripts\activate  # CMD
```

### 3. Cài dependencies

```bash
pip install -r requirements.txt
```

### 4. Tạo database MySQL

```sql
CREATE DATABASE pbmed CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Cấu hình `.env`

Tạo file `.env` trong thư mục gốc:

```env
SECRET_KEY=django-insecure-your-secret-key-here
DB_NAME=pbmed
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

### 6. Migrate & seed data

```bash
python manage.py setup
```

Lệnh này tự động migrate database và tạo dữ liệu mẫu.

---

## Tài khoản mẫu

| Vai trò | Username | Mật khẩu |
|---------|----------|----------|
| Quản trị | admin | 123456 |
| Bác sĩ | doc001 — doc005 | 123456 |
| Lễ tân | reception01 — reception02 | 123456 |
| Bệnh nhân | patient01 — patient05 | 123456 |

---

## Cấu trúc project

```
Hospital-Management-main/
├── manage.py                 # Entry point Django
├── requirements.txt          # Dependencies
├── .env                      # Biến môi trường
├── .env.example              # Mẫu .env
│
├── hospital/                 # Cấu hình Django
│   ├── settings.py
│   ├── urls.py               # Router chính
│   └── wsgi.py / asgi.py
│
├── users/                    # App: Người dùng
│   ├── models.py             # User, Doctors, Patients, Specialty...
│   ├── views.py              # Login, register, forgot/reset pass
│   ├── helpers.py            # Gửi email
│   ├── urls.py
│   └── management/commands/
│       └── setup.py          # Seed data bằng ORM
│
├── patients/                 # App: Bệnh nhân
│   ├── models.py             # Appointment, PatientProfile, CLS...
│   ├── views.py              # Đặt lịch, hồ sơ, lịch sử khám
│   └── urls.py
│
├── doctors/                  # App: Bác sĩ
│   ├── views.py              # Dashboard, lịch hẹn, phiếu khám, CLS
│   └── urls.py
│
├── receptionist/             # App: Lễ tân
│   ├── views.py              # Dashboard, walk-in, lịch hẹn
│   └── urls.py
│
├── administration/           # App: Quản trị
│   ├── views.py              # Quản lý user, danh mục, báo cáo CSV
│   └── urls.py
│
└── templates/                # Giao diện
    ├── users/                # Login, register, forgot/reset
    ├── patients/             # Đặt lịch, hồ sơ, lịch sử
    ├── doctors/              # Dashboard, phiếu khám, CLS
    ├── receptionist/         # Dashboard, lịch hẹn, walk-in
    └── administration/       # Quản lý, báo cáo
```

---

## Chức năng chính

### Bệnh nhân
- Đăng ký, đăng nhập, quên mật khẩu
- Đặt lịch hẹn khám theo chuyên khoa
- Quản lý hồ sơ cá nhân
- Xem lịch sử khám bệnh & kết quả CLS

### Bác sĩ
- Dashboard thống kê (hôm nay, tuần, tháng)
- Quản lý lịch hẹn (xác nhận/hủy)
- Tạo & chỉnh sửa phiếu khám
- Chỉ định & nhập kết quả CLS
- Xem danh sách bệnh nhân đã khám

### Lễ tân
- Dashboard lịch hẹn hôm nay
- Xác nhận/hủy lịch hẹn
- Đăng ký khám trực tiếp (walk-in)
- Xem lịch bác sĩ trong tuần

### Quản trị
- Dashboard tổng quan
- Quản lý tài khoản người dùng (CRUD)
- Quản lý danh mục (chuyên khoa, dịch vụ CLS)
- Báo cáo thống kê & xuất CSV

---

## Chạy server

```bash
python manage.py runserver
```

Truy cập: **http://localhost:8000/**
