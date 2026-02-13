from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from accounts.models import Hotel, Booking, HotelUser
from home.forms import BookingForm

# Create your views here.

def index(request):
    hotels = Hotel.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        hotels = hotels.filter(
            Q(hotel_name__icontains=search_query) |
            Q(hotel_description__icontains=search_query) |
            Q(hotel_location__icontains=search_query)
        )
    
    context = {
        'hotels': hotels,
        'search_query': search_query,
        'total_hotels': Hotel.objects.filter(is_active=True).count(),
        'filtered_count': hotels.count()
    }
    
    return render(request, 'index.html', context)


def hotel_detail(request, hotel_slug):
    hotel = Hotel.objects.filter(hotel_slug=hotel_slug, is_active=True).first()
    
    if not hotel:
        return render(request, '404.html', status=404)
    
    images = hotel.hotel_images.all()
    booking_form = BookingForm()
    
    context = {
        'hotel': hotel,
        'images': images,
        'booking_form': booking_form,
    }
    
    return render(request, 'hotel_detail.html', context)


def create_booking(request, hotel_slug):
    """Handle booking creation with login check"""
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login or register to book a hotel')
        return redirect('register')
    
    # Get the actual HotelUser instance
    try:
        guest = HotelUser.objects.get(id=request.user.id)
    except HotelUser.DoesNotExist:
        messages.error(request, 'Your account is not properly configured. Please register again.')
        return redirect('register')
    
    hotel = get_object_or_404(Hotel, hotel_slug=hotel_slug, is_active=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        
        if form.is_valid():
            # Validate dates
            check_in = form.cleaned_data['check_in_date']
            check_out = form.cleaned_data['check_out_date']
            
            if check_in >= check_out:
                messages.error(request, 'Check-out date must be after check-in date')
                return redirect('hotel_detail', hotel_slug=hotel_slug)
            
            if check_in < datetime.now().date():
                messages.error(request, 'Check-in date cannot be in the past')
                return redirect('hotel_detail', hotel_slug=hotel_slug)
            
            # Calculate total price
            num_nights = (check_out - check_in).days
            price_per_night = hotel.hotel_offer_price if hotel.hotel_offer_price else hotel.hotel_price
            total_price = price_per_night * form.cleaned_data['number_of_rooms'] * num_nights
            
            # Create booking
            booking = form.save(commit=False)
            booking.guest = guest
            booking.hotel = hotel
            booking.total_price = total_price
            booking.save()
            
            messages.success(request, 'Booking created successfully!')
            return redirect('booking_detail', booking_id=booking.id)
        else:
            messages.error(request, 'Please fill in all required fields correctly')
            return redirect('hotel_detail', hotel_slug=hotel_slug)
    
    return redirect('hotel_detail', hotel_slug=hotel_slug)


@login_required(login_url='register')
def my_bookings(request):
    """Display all bookings for the logged-in user"""
    
    bookings = Booking.objects.filter(guest=request.user).prefetch_related('hotel')
    
    context = {
        'bookings': bookings
    }
    
    return render(request, 'my_bookings.html', context)


@login_required(login_url='register')
def booking_detail(request, booking_id):
    """Display details of a specific booking"""
    
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)
    
    context = {
        'booking': booking
    }
    
    return render(request, 'booking_detail.html', context)


@login_required(login_url='register')
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)
    
    if booking.booking_status == 'cancelled':
        messages.warning(request, 'Booking is already cancelled')
    elif booking.booking_status == 'completed':
        messages.error(request, 'Cannot cancel a completed booking')
    else:
        booking.booking_status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully')
    
    return redirect('my_bookings')
