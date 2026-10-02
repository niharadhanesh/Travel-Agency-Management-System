from django.shortcuts import render


def home(request):
    return render(request, 'home.html')
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def home(request):
    return render(request, 'home.html')

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
            return redirect('home')
        error = 'Invalid username or password.'
    return render(request, 'login.html', {'error': error})