import os
import django
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oyo_clone.settings')
django.setup()

from accounts.models import HotelVendor, Hotel, Ameneties
from django.utils.text import slugify

fake = Faker()

# Create or get a default vendor if none exists
vendor_exists = HotelVendor.objects.exists()
if not vendor_exists:
    # Create a default vendor
    default_vendor = HotelVendor.objects.create_user(
        username='default_vendor',
        email='vendor@oyoclone.com',
        password='vendor123',
        phone_number='9999999999',
        buisness_name='OYO Hotels Default'
    )
    print(f"Created default vendor: {default_vendor.username}")
else:
    default_vendor = HotelVendor.objects.first()

# Get or create amenities
amenity_list = [
    'WiFi', 'AC', 'TV', 'Swimming Pool', 'Gym', 'Parking', 
    'Restaurant', 'Room Service', 'Laundry', 'Front Desk 24/7',
    'Hot Water', 'Air Conditioning', 'Mini Bar', 'Iron & Board'
]

amenities = []
for amenity_name in amenity_list:
    amenity, created = Ameneties.objects.get_or_create(
        amenetie_name=amenity_name,
        defaults={'icon': 'hotel/default.jpg'}
    )
    amenities.append(amenity)

print(f"Amenities created/retrieved: {len(amenities)}")

# Cities for hotels
cities = [
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
    'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
    'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte',
    'San Francisco', 'Indianapolis', 'Seattle', 'Denver', 'Washington DC'
]

# Hotel name prefixes
hotel_prefixes = [
    'Grand', 'Royal', 'Palace', 'Imperial', 'Plaza',
    'Tower', 'Crown', 'Majestic', 'Elite', 'Prestige',
    'Luxury', 'Heritage', 'Regency', 'Metropolitan', 'Continental'
]

# Generate 200 hotels
print("Generating 200 hotels...")
existing_count = Hotel.objects.count()

if existing_count < 200:
    hotels_to_create = 200 - existing_count
    
    for i in range(hotels_to_create):
        hotel_name = f"{fake.random_element(hotel_prefixes)} Hotel {i+1+existing_count}"
        hotel_slug = slugify(hotel_name + '-' + fake.word())
        
        # Ensure slug is unique
        counter = 1
        original_slug = hotel_slug
        while Hotel.objects.filter(hotel_slug=hotel_slug).exists():
            hotel_slug = f"{original_slug}-{counter}"
            counter += 1
        
        hotel_location = fake.city() + ', ' + fake.random_element(cities)
        hotel_price = float(fake.random_int(min=1000, max=10000))
        hotel_offer_price = hotel_price * fake.random.uniform(0.7, 0.95)
        
        hotel = Hotel.objects.create(
            hotel_name=hotel_name,
            hotel_description=fake.paragraph(nb_sentences=5),
            hotel_slug=hotel_slug,
            hotel_owner=default_vendor,
            hotel_price=hotel_price,
            hotel_offer_price=hotel_offer_price,
            hotel_location=hotel_location,
            is_active=True
        )
        
        # Add random amenities
        random_amenities = fake.random_elements(amenities, length=fake.random_int(min=3, max=8), unique=True)
        hotel.ameneties.set(random_amenities)
        
        if (i + 1) % 20 == 0:
            print(f"Created {i + 1} hotels...")
    
    print(f"Successfully created {hotels_to_create} hotels!")
    print(f"Total hotels in database: {Hotel.objects.count()}")
else:
    print(f"Database already has {existing_count} hotels. Skipping creation.")
