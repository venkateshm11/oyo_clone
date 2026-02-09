
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
from .models import Hotel

def generateRandomToken():
    return str(uuid.uuid4())

def sendEmailToken(email, token):
    subject = 'Please verify your email'
    message = f"""Please verify your email by clicking the link below:
            http://localhost:8000/accounts/verify-email/{token}/
            """
            
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
)

def sendOTPtoMail(email, otp):
    subject = 'Your OTP for OYO Login'
    message = f"""Your One-Time Password (OTP) for logging into OYO is: {otp}
    
    This OTP is valid for 10 minutes. Please do not share it with anyone.
    
    If you did not request this OTP, please ignore this email.
    """
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
)   
    

def generateSlug(hotel_name):
    slug = slugify(hotel_name) + "-" + str(uuid.uuid4()).split('-')[0]

    if Hotel.objects.filter(hotel_slug=slug).exists():
        return generateSlug(hotel_name)

    return slug