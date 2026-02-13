
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.db import IntegrityError
from accounts.models import Hotel, HotelUser, HotelVendor, Ameneties, HotelImages
from django.contrib import messages
from accounts.utils import generateRandomToken
from accounts.utils import sendEmailToken, sendOTPtoMail
import random
from django.contrib.auth.decorators import login_required
from .utils import generateSlug




# Create your views here.


def login_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        user = authenticate(request, username=phone_number, password=password)

        if not user:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

        # ✅ SAFE CHECK
        if hasattr(user, 'is_verified') and not user.is_verified:
            messages.warning(request, 'Please verify your email first')
            return redirect('login')

        login(request, user)
        messages.success(request, 'Login successful')
        return redirect('index')

    return render(request, 'login.html')

    
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        # ensure email/phone are unique across both user types
        if HotelUser.objects.filter(email=email).exists() or HotelVendor.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists')
            return render(request, 'register.html')

        if HotelUser.objects.filter(username=phone_number).exists() or HotelVendor.objects.filter(username=phone_number).exists():
            messages.warning(request, 'Phone number already registered')
            return render(request, 'register.html')

        try:
            token = generateRandomToken()

            HotelUser.objects.create_user(
                username=phone_number,   # 🔥 phone is username
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                password=password,
                email_token=token
            )

            sendEmailToken(email, token)
            messages.success(request, 'Account created. Verify your email.')
            return redirect('login')

        except IntegrityError:
            messages.error(request, 'User already exists')

    return render(request, 'register.html')


def verify_email(request, token):
    # support verifying either HotelUser or HotelVendor
    user = HotelUser.objects.filter(email_token=token).first()
    if user:
        user.is_verified = True
        user.email_token = None
        user.save()
        messages.success(request, 'Email verified successfully')
        return redirect('login')

    vendor = HotelVendor.objects.filter(email_token=token).first()
    if vendor:
        # HotelVendor model doesn't have is_verified flag in this schema,
        # but clearing the token and acknowledging verification is useful
        vendor.email_token = None
        vendor.save()
        messages.success(request, 'Vendor email verified successfully')
        return redirect('vendor_login')

    messages.warning(request, 'Invalid or expired token')
    return redirect('login')


def send_otp(request, email):
    user = HotelUser.objects.filter(email=email).first()

    if not user:
        messages.warning(request, 'Email not registered')
        return redirect('login')

    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.save()

    sendOTPtoMail(email, otp)
    messages.success(request, 'OTP sent to your email')
    return redirect('verify_otp', email=email)


def verify_otp(request, email):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user = HotelUser.objects.filter(email=email).first()

        if user and user.otp == otp:
            user.otp = None
            user.save()
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('index')

        messages.warning(request, 'Invalid OTP')

    return render(request, 'utils/verify_otp.html')





    
    
def vendor_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        # ensure email/phone not used by any user/vendor
        if HotelUser.objects.filter(email=email).exists() or HotelVendor.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists')
            return render(request, 'vendor_register.html')

        if HotelUser.objects.filter(username=phone_number).exists() or HotelVendor.objects.filter(username=phone_number).exists():
            messages.warning(request, 'Phone number already registered')
            return render(request, 'vendor_register.html')

        token = generateRandomToken()

        # create a HotelVendor record for vendor accounts
        user = HotelVendor.objects.create_user(
            username=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password=password,
            email_token=token,
            buisness_name=business_name
        )

        sendEmailToken(email, token)
        messages.success(request, 'Vendor account created. Verify email.')
        return redirect('vendor_login')

    return render(request, 'vendor_register.html')


def vendor_login(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        user = authenticate(request, username=phone_number, password=password)

        if not user:
            messages.error(request, 'Invalid credentials')
            return redirect('vendor_login')

        # fetch the HotelVendor instance directly (authenticate may return base User class)
        vendor = HotelVendor.objects.filter(username=phone_number).first()
        
        if not vendor:
            # check if it's a HotelUser with is_vendor flag
            user_obj = HotelUser.objects.filter(username=phone_number, is_vendor=True).first()
            if user_obj:
                user = user_obj
            else:
                messages.error(request, 'Not a vendor account')
                return redirect('vendor_login')
        else:
            user = vendor

        # if the user model supports verification, enforce it
        if getattr(user, 'is_verified', True) is False:
            messages.warning(request, 'Verify your email first')
            return redirect('vendor_login')

        login(request, user)
        messages.success(request, 'Vendor login successful')
        return redirect('vendor_dashboard')
    

    return render(request, 'vendor_login.html')


@login_required(login_url='vendor_login')
def vendor_dashboard(request):
    context = {'hotels': Hotel.objects.filter(hotel_owner=request.user)}
    return render(request, 'vendor_dashboard.html', context)

@login_required(login_url='vendor_login')
def add_hotel(request):
    ameneties = Ameneties.objects.all()
    
    if request.method == 'POST':
        # handle hotel addition logic here
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description') 
        hotel_price = request.POST.get('hotel_price') 
        ameneties = request.POST.getlist('hotel_ameneties')  # assuming this is a list of amenetie IDs 
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')  # assuming this is a list of amenetie IDs
        hotel_slug = generateSlug(hotel_name)

        hotel_vendor = HotelVendor.objects.get(id=request.user.id)

        # Get the vendor instance - could be HotelVendor or HotelUser with is_vendor flag
        vendor = None
        if isinstance(request.user, HotelVendor):
            vendor = request.user
        else:
            # Try to get as HotelVendor
            vendor = HotelVendor.objects.filter(username=request.user.username).first()
        
        if not vendor:
            messages.error(request, 'Invalid vendor account')
            return redirect('vendor_dashboard')

        hotel_obj = Hotel.objects.create(
            hotel_name=hotel_name,
            hotel_description=hotel_description,
            hotel_slug=hotel_slug,
            hotel_owner=hotel_vendor,
            hotel_price=hotel_price,
            hotel_offer_price=hotel_offer_price,
            hotel_location=hotel_location,
            
        )
        for ameneti in ameneties:
            ameneti = Ameneties.objects.get(id=ameneti)
            hotel_obj.ameneties.add(ameneti)
            hotel_obj.save()
        
        
        messages.success(request, 'Hotel added successfully', extra_tags='hotel')
        return redirect('vendor_dashboard')
    

    return render(request, 'add_hotel.html', context={'ameneties': ameneties})



@login_required(login_url='vendor_login')
def add_hotel_image(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    # ensure the logged-in vendor owns this hotel
    if hotel.hotel_owner.id != request.user.id:
        messages.error(request, 'You do not have permission to modify this hotel')
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        image = request.FILES.get('image')
        if not image:
            messages.error(request, 'No image uploaded', extra_tags='hotel')
            return redirect('vendor_dashboard')

        HotelImages.objects.create(hotel_owner=hotel, image=image)
        messages.success(request, 'Image added successfully', extra_tags='hotel')
        return redirect('vendor_dashboard')

    return redirect('vendor_dashboard')


    return render(request, 'edit_hotel_image.html', {'image': img})
@login_required(login_url='vendor_login')
def edit_hotel(request, hotel_id): 
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if hotel.hotel_owner.id != request.user.id:
        messages.error(request, 'You do not have permission to edit this hotel')
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price = request.POST.get('hotel_price')
        ameneties = request.POST.getlist('hotel_ameneties') # assuming this is a list of amenetie IDs
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location') # assuming this is a list of amenetie IDs
        hotel.hotel_name = hotel_name
        hotel.hotel_description = hotel_description
        hotel.hotel_price = hotel_price
        hotel.hotel_offer_price = hotel_offer_price
        hotel.hotel_location = hotel_location
        hotel.ameneties.set(Ameneties.objects.filter(id__in=ameneties))
        hotel.save()
        messages.success(request, 'Hotel updated successfully', extra_tags='hotel')
        return redirect('vendor_dashboard')

    context = {
        'hotel': hotel,
        'ameneties': Ameneties.objects.all(),
    }
    return render(request, 'edit_hotel.html', context)

@login_required(login_url='vendor_login')
def delete_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if hotel.hotel_owner.id != request.user.id:
        messages.error(request, 'You do not have permission to delete this hotel')
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        hotel.delete()
        messages.success(request, 'Hotel deleted', extra_tags='hotel')
        return redirect('vendor_dashboard')

    # If GET, show a simple confirm page or redirect back
    return redirect('vendor_dashboard')

@login_required(login_url='vendor_login')
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('index')