# PBMed 🏥

**PBMed-Hospital Management System** 

---
**Sinh viên:** Hoàng Minh Nhất — **MSSV: 20237468**  
## Giới thiệu

Hệ thống quản lý bệnh viện với 4 vai trò: **Admin**, **Bác sĩ**, **Lễ tân**, **Bệnh nhân**.  
Hỗ trợ đặt lịch hẹn, khám bệnh, chỉ định CLS, thống kê báo cáo.
 
**Công nghệ:** Django 5.2 + MySQL 9.3 + Bootstrap 5.3

---

## Tính năng chính

| Vai trò | Tính năng |
|---------|-----------|
| 🔐 Admin | Quản lý tài khoản, danh mục, thống kê, xuất báo cáo CSV |
| 🩺 Bác sĩ | Khám bệnh, tạo phiếu khám, chỉ định CLS, xem lịch hẹn |
| 📋 Lễ tân | Xác nhận/hủy lịch hẹn, tạo lịch hẹn trực tiếp |
| 👤 Bệnh nhân | Đặt lịch hẹn, xem lịch sử khám, kết quả CLS |

---

## Cài đặt nhanh

### Yêu cầu
- Python 3.11+, MySQL 9.3

### 1. Clone & vào thư mục
```bash
git clone https://github.com/nhatminh0113/PBMed-_-Hospital-Management.git
cd PBMed-_-Hospital-Management
```

### 2. Môi trường & dependencies
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Tạo database
```sql
CREATE DATABASE pbmed CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Migrate & Seed data
```bash
python manage.py migrate
python manage.py setup
```

### 5. Chạy
```bash
python manage.py runserver
# http://localhost:8000
```

---

## Tài khoản mẫu (mật khẩu: `123456`)

| Vai trò | Username | Mô tả |
|---------|----------|-------|
| Admin | `admin` | Quản trị hệ thống |
| Bác sĩ | `doc001` → `doc005` | 5 bác sĩ các chuyên khoa |
| Lễ tân | `reception01` → `reception02` | 2 lễ tân |
| Bệnh nhân | `patient01` → `patient05` | 5 bệnh nhân |

---

## Cấu trúc thư mục

```
PBMed/
├── hospital/              # Django settings
├── users/                 # Tài khoản, bác sĩ, lễ tân
├── patients/              # Bệnh nhân, lịch hẹn, khám bệnh, CLS
├── doctors/               # Giao diện bác sĩ
├── receptionist/          # Giao diện lễ tân
├── administration/        # Giao diện admin
├── templates/             # Giao diện (Bootstrap)
├── static/                # Ảnh, CSS, JS
├── seed/                  # Fixtures (danh mục)
├── seed_data.sql          # Dữ liệu mẫu (20 bảng)
└── requirements.txt       # Python packages
```

---

## Ghi chú

- Dữ liệu demo được backup trong `seed_data.sql`
- Chạy `python manage.py setup` để tạo lại dữ liệu mẫu
