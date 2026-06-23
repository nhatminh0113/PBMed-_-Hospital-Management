from django.core.mail import send_mail
from django.conf import settings

def send_email(email,token):
    subject = 'PBMed - Đặt lại mật khẩu'
    message = f'Vui lòng nhấp vào link sau để đặt lại mật khẩu:\n\nhttp://127.0.0.1:8000/reset/{token}/\n\nLink có hiệu lực trong 24 giờ.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    try:
        send_mail(subject,message,email_from,recipient_list)
        return True
    except Exception:
        return False