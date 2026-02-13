from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class HotelUser(User):
    phone_number = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to='profile', null=True, blank=True)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)  # 🔥 IMPORTANT
    buisness_name = models.CharField(max_length=200, null=True, blank=True)



class HotelVendor(User):
    phone_number = models.CharField(max_length=15,unique=True)
    profile_picture = models.ImageField(upload_to='profile')
    email_token = models.CharField(max_length=100, null=True, blank=True)
    buisness_name = models.CharField(max_length=200, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)


class Ameneties(models.Model):
    amenetie_name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='hotel')


class Hotel(models.Model):
    hotel_name = models.CharField(max_length=200)
    hotel_description = models.TextField()
    hotel_slug = models.SlugField(max_length=1000, unique=True)
    hotel_owner = models.ForeignKey(HotelVendor, on_delete=models.CASCADE, related_name='hotels')
    ameneties = models.ManyToManyField(Ameneties, related_name='hotels_with_ameneties')
    hotel_price = models.FloatField()
    hotel_offer_price = models.FloatField(null=True, blank=True)
    hotel_location = models.CharField(max_length=300)
    is_active = models.BooleanField(default=False)

    


class HotelImages(models.Model):
    hotel_owner = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_images')
    image = models.ImageField(upload_to='hotel')


class HotelManager(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='managers')
    manager_name = models.CharField(max_length=200)
    manager_contact = models.CharField(max_length=15)


class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    guest = models.ForeignKey(HotelUser, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_rooms = models.PositiveIntegerField(default=1)
    number_of_guests = models.PositiveIntegerField(default=1)
    total_price = models.FloatField()
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    special_requests = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking: {self.guest.first_name} - {self.hotel.hotel_name}"
    
    class Meta:
        ordering = ['-created_at']

