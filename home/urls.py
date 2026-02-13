from django.contrib import admin
from django.urls import path
from home.views import index, hotel_detail, create_booking, my_bookings, booking_detail, cancel_booking

urlpatterns = [
    path('', index, name='index'),
    path('hotel/<slug:hotel_slug>/', hotel_detail, name='hotel_detail'),
    path('hotel/<slug:hotel_slug>/book/', create_booking, name='create_booking'),
    path('my-bookings/', my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/', booking_detail, name='booking_detail'),
    path('booking/<int:booking_id>/cancel/', cancel_booking, name='cancel_booking'),
]
