
from django.contrib import admin
from django.urls import path
from .views import add_hotel, login_view, register, send_otp, vendor_dashboard, vendor_login, vendor_register, verify_otp, add_hotel_image, edit_hotel_image, delete_hotel

urlpatterns = [
    path('send_otp/<str:email>/', send_otp, name='send_otp'),
    path('verify_otp/<str:email>/', verify_otp, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'), 
    path('vendor_login/', vendor_login, name='vendor_login'),
    path('vendor_register/', vendor_register, name='vendor_register'),
    path('vendor_dashboard/', vendor_dashboard, name='vendor_dashboard'),
    path('add_hotel/', add_hotel, name='add_hotel'),
    path('hotel/<int:hotel_id>/add_image/', add_hotel_image, name='add_hotel_image'),
    path('hotel/<int:hotel_id>/edit_image/', edit_hotel_image, name='edit_hotel_image'),
    path('hotel/<int:hotel_id>/delete/', delete_hotel, name='delete_hotel'),
]
