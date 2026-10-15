from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404

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