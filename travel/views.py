from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from datetime import date, timedelta

from .models import Booking

from .destination_data import DESTINATIONS


# ---------- Public pages ----------

def home(request):
    return render(request, 'home.html')


def destinations(request):
    return render(request, 'destinations.html')


@login_required(login_url='signup')
def destination_detail(request, slug):
    place = DESTINATIONS.get(slug)
    if place is None:
        raise Http404('Destination not found')

    # next three destinations (wraps around) for the "More places" row
    slugs = list(DESTINATIONS)
    i = slugs.index(slug)
    related = [DESTINATIONS[slugs[(i + n) % len(slugs)]] for n in (1, 2, 3)]

    return render(request, 'destination_detail.html', {'place': place, 'related': related})


# ---------- Authentication ----------

def signup(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password != confirm:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error = 'That username is already taken.'
        elif User.objects.filter(email=email).exists():
            error = 'An account with that email already exists.'
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            login(request, user)
            return redirect('customer_dashboard')

    return render(request, 'signup.html', {'error': error})


def login_view(request):
    error = None

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )

        if user is not None:
            login(request, user)

            # SuperAdmin -> admin dashboard
            if user.is_superuser:
                return redirect('dashboard')

            # Customer -> customer dashboard
            return redirect('customer_dashboard')

        error = 'Invalid username or password.'

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------- Dashboards ----------

@login_required(login_url='login')
def dashboard(request):
    # Admin dashboard: only SuperAdmin can access
    if not request.user.is_superuser:
        return redirect('customer_dashboard')

    return render(request, 'dashboard.html')


@login_required(login_url='login')
def customer_dashboard(request):
    # Customer dashboard: SuperAdmin goes to the admin dashboard instead
    if request.user.is_superuser:
        return redirect('dashboard')

    return render(request, 'customer_dashboard.html')


@login_required(login_url='login')
def customer_destinations(request):
    if request.user.is_superuser:
        return redirect('dashboard')

    return render(request, 'customer_destinations.html')


@login_required(login_url='login')
def book_trip(request, slug):
    if request.user.is_superuser:
        return redirect('dashboard')

    place = DESTINATIONS.get(slug)
    if place is None:
        raise Http404('Destination not found')

    unit_price = int(place['price'].replace(',', ''))
    min_date = date.today() + timedelta(days=1)
    error = None
    values = {}

    if request.method == 'POST':
        values = request.POST
        try:
            travellers = int(request.POST.get('travellers', 0))
            travel_date = date.fromisoformat(request.POST.get('travel_date', ''))
        except ValueError:
            travellers, travel_date = 0, None

        phone = request.POST.get('phone', '').strip()

        if travel_date is None or travel_date < min_date:
            error = 'Please choose a travel date from tomorrow onwards.'
        elif not 1 <= travellers <= 10:
            error = 'Travellers must be between 1 and 10.'
        elif len(phone) < 7:
            error = 'Please enter a valid phone number.'
        else:
            booking = Booking.objects.create(
                user=request.user,
                destination_slug=slug,
                destination_name=place['name'],
                travel_date=travel_date,
                travellers=travellers,
                full_name=request.POST.get('full_name', '').strip(),
                email=request.POST.get('email', '').strip(),
                phone=phone,
                notes=request.POST.get('notes', '').strip(),
                total_amount=unit_price * travellers,
            )
            return render(request, 'booking.html', {'place': place, 'booking': booking})

    return render(request, 'booking.html', {
        'place': place,
        'unit_price': unit_price,
        'min_date': min_date,
        'values': values,
        'error': error,
    })
    
@login_required(login_url='login')
def my_bookings(request):
    if request.user.is_superuser:
        return redirect('dashboard')

    bookings = list(Booking.objects.filter(user=request.user))
    for b in bookings:
        place = DESTINATIONS.get(b.destination_slug)
        b.thumb = place['thumb'] if place else ''

    active = [b for b in bookings if b.status != 'cancelled']
    return render(request, 'customer_bookings.html', {
        'bookings': bookings,
        'total_count': len(bookings),
        'confirmed_count': sum(b.status == 'confirmed' for b in bookings),
        'pending_count': sum(b.status == 'pending' for b in bookings),
        'total_value': sum(b.total_amount for b in active),
    })