
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def home(request):
    return render(request, 'home.html')

# views.py
def destinations(request):
    return render(request, 'destinations.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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

            # SuperAdmin
            if user.is_superuser:
                return redirect('dashboard')

            # Normal user
            return redirect('home')

        error = 'Invalid username or password.'

    return render(request, 'login.html', {'error': error})


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required(login_url='login')
def admin_dashboard(request):
    # Only SuperAdmin can access this dashboard
    if not request.user.is_superuser:
        return redirect('home')

    return render(request, 'dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')