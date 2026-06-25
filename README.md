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

---

## Cài đặt

### Yêu cầu
- **Python 3.11+** — [tải tại python.org](https://python.org)
- **MySQL 8+** — [tải tại mysql.com](https://mysql.com)
- **Git** — [tải tại git-scm.com](https://git-scm.com)

### Các bước

#### Bước 1: Mở terminal
- Windows: mở **Git Bash** (chuột phải trong thư mục → Git Bash Here) hoặc **Command Prompt** (CMD)
- Mac/Linux: mở **Terminal**

#### Bước 2: Tải code từ GitHub
```bash
git clone https://github.com/nhatminh0113/PBMed-_-Hospital-Management.git
cd PBMed-_-Hospital-Management
```
> **Giải thích:** `git clone` tải toàn bộ mã nguồn về máy. `cd` di chuyển vào thư mục project.

#### Bước 3: Tạo môi trường ảo
```bash
python -m venv venv
```
> **Giải thích:** Tạo một "khoang riêng" cho Python của project này, không ảnh hưởng tới các project khác. Thư mục `venv/` được tạo ra để chứa Python riêng.

Kích hoạt môi trường ảo (tuỳ terminal bạn dùng):

**Git Bash:**
```bash
source venv/Scripts/activate
```

**CMD (Command Prompt):**
```cmd
venv\Scripts\activate
```

> Sau khi kích hoạt, bạn sẽ thấy chữ `(venv)` xuất hiện ở đầu dòng — báo hiệu đang dùng môi trường ảo.

#### Bước 4: Cài thư viện
```bash
pip install -r requirements.txt
```
> **Giải thích:** `requirements.txt` là danh sách các thư viện project cần (Django, mysqlclient, python-dotenv...). Lệnh này cài tất cả. Thư viện sẽ nằm trong thư mục `venv/` — không ảnh hưởng Python hệ thống.

#### Bước 5: Thiết lập toàn bộ (tự động)
```bash
python manage.py setup
```
> **Lệnh này tự động làm 4 việc:**
> 1. **Tạo file `.env`** — copy từ `.env.example`, tự sinh khoá bí mật Django
> 2. **Tạo database MySQL** — kết nối MySQL, tạo database `pbmed` nếu chưa có
> 3. **Migrate** — tạo các bảng (tables) trong database
> 4. **Seed** — nạp dữ liệu mẫu (tài khoản, lịch hẹn, phiếu khám...)

> ⚠️ **Nếu MySQL có password:** lần đầu chạy `setup` sẽ báo lỗi. Mở file `.env` bằng Notepad, sửa dòng `DB_PASSWORD=***` thành password MySQL của bạn, rồi chạy lại `setup`.

#### Bước 6: Chạy server
```bash
python manage.py runserver
```
> Mở trình duyệt, truy cập **http://localhost:8000/**
> `manage.py` là file điều khiển Django. `runserver` khởi động server phát triển.

---

## Tài khoản mẫu

| Vai trò | Username | Mật khẩu |
|---------|----------|----------|
| Quản trị | admin | 123456 |
| Bác sĩ | doc001 — doc005 | 123456 |
| Lễ tân | reception01 — reception02 | 123456 |
| Bệnh nhân | patient01 — patient05 | 123456 |

> Tất cả tài khoản đều do lệnh `setup` tự động tạo.

---

## Cấu trúc project

```
PBMed-_-Hospital-Management/
├── manage.py                 # Entry point Django
├── requirements.txt          # Danh sách thư viện cần cài
├── .env                      # Biến môi trường (tạo tự động bởi setup)
├── .env.example              # Mẫu .env (dùng để tạo .env)
│
├── hospital/                 # Cấu hình Django
│   ├── settings.py
│   ├── urls.py               # Router URL chính
│   └── wsgi.py / asgi.py
│
├── users/                    # App: Người dùng
│   ├── models.py             # User, Doctors, Patients, Specialty...
│   ├── views.py              # Login, register, forgot/reset pass
│   ├── helpers.py            # Gửi email
│   ├── urls.py
│   └── management/commands/
│       └── setup.py          # Tự động: .env → DB → migrate → seed
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

### Lễ tân
- Dashboard lịch hẹn hôm nay
- Xác nhận/hủy lịch hẹn
- Đăng ký khám trực tiếp (walk-in)

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
