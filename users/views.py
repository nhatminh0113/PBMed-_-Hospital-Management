from django.shortcuts import render

from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from .models import Doctors, Patients, Reste_token, Specialty
from .helpers import send_email
import uuid


Users = get_user_model()

def register(request):
  if request.method == 'POST':
    first_name = request.POST.get('user_firstname')
    last_name = request.POST.get('user_lastname')

    username = request.POST.get('user_id')
    email = request.POST.get('email')
    gender = request.POST.get('user_gender')
    birthday = request.POST.get("birthday") or None
    password = request.POST.get('password')
    confirm_password = request.POST.get('conf_password')

    if len(password) < 6:
      messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự.')
      return render(request, 'users/register.html', context={'user_firstname': first_name, 'user_lastname': last_name, 'user_id': username, 'email': email, 'user_gender': gender})

    if password != confirm_password:
      messages.error(request, 'Mật khẩu không khớp.')
      return render(request, 'users/register.html', context={'user_firstname': first_name, 'user_lastname': last_name, 'user_id': username, 'email': email, 'user_gender': gender})

    if Users.objects.filter(username=username).exists():
      messages.error(request, 'Tên đăng nhập đã tồn tại.')
      return render(request, 'users/register.html', context={'user_firstname': first_name, 'user_lastname': last_name, 'user_id': username, 'email': email, 'user_gender': gender})

    user = Users.objects.create_user(
      first_name=first_name,
      last_name=last_name,
      username=username,
      email=email,
      gender=gender,
      birthday=birthday,
      password=password,
      is_doctor=False
    )
      
    user.save()

    patient = Patients.objects.create(user=user)
    patient.save()

    messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.', extra_tags='success')
    return redirect('login')

  return render(request, 'users/register.html')


def login_view(request):
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
      login(request, user)

      if user.is_doctor:
        return redirect('doctor_dashboard')

      elif user.is_admin:
        return redirect('admin_dashboard')

      elif user.is_receptionist:
        return redirect('receptionist_dashboard')

      elif Patients.objects.filter(user=user).exists():
        return redirect('book_appointment')
    else:
      messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu')
      
    return render(request, 'users/login.html')
  
  return render(request, 'users/login.html')


def forgot_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = Users.objects.filter(email=email)
        if user:
            token = str(uuid.uuid4())
            reset = Reste_token.objects.create(
                user=user[0],
                email=user[0].email,  
                token=token  
            )
            reset.save()
            sent = send_email(user[0].email,token)
            if sent:
                return render(request, 'users/forgot.html',context={'send_email_succes': 1})
        else:
            return render(request, 'users/forgot.html', context={'errorlogin': 1})
    return render(request, 'users/forgot.html')

def reset_view(request,token):
    if request.method == 'POST':
        reste = Reste_token.objects.filter(token=token)
        print(reste)
        if reste:
            password = request.POST.get('password')
            confirm_password = request.POST.get('conf_password')
            if len(password) < 6:
                messages.error(request, 'Password must be at least 6 characters long.')
                return render(request, 'users/reset.html', {'token': token} )
            print(password)
            print(confirm_password)
            if password != confirm_password:
                messages.error(request, 'password do not match')
                return render(request, 'users/reset.html', {'token': token} )
            user = Users.objects.filter(email=reste[0].email).first()
            if user:
                hashed_password = make_password(password)
                user.password = hashed_password
                user.save()
                reste.delete()
                return redirect('login')
            else:
                return render(request, 'users/reset.html', {'token': token , 'errorlogin':1} )
        return render(request, 'users/reset.html', {'token': token} )
    return render(request, 'users/reset.html',{'token': token})


@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('login')
