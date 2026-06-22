# PBMed - Hospital Management System

He thong quan ly benh vien (do an tot nghiep).

## Yeu cau
- Python 3.11+
- MySQL 9.3
- Git

## Cai dat

### 1. Clone du an
git clone <your-repo-url>
cd Hospital-Management-main

### 2. Tao moi truong ao
python -m venv venv
venv\Scriptsctivate      (Windows)

### 3. Cai dependencies
pip install -r requirements.txt

### 4. Tao database
Mo MySQL Workbench hoac HeidiSQL, chay:
CREATE DATABASE pbmed CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

### 5. Migrate + Seed data
python manage.py migrate
python manage.py setup

### 6. Chay web
python manage.py runserver
Vao http://localhost:8000

## Tai khoan mau
- Admin:      admin / 123456
- Bac si:     doc001-doc005 / 123456
- Le tan:     reception01-reception02 / 123456
- Benh nhan:  patient01-patient05 / 123456

## Ghi chu
- File seed_data.sql chua toan bo data mau (20 tables)
- Data duoc luu trong MySQL, khong trong GitHub
