from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('destinations/', views.destinations, name='destinations'),
    path('destinations/<slug:slug>/', views.destination_detail, name='destination_detail'),

    path('book/<slug:slug>/', views.book_trip, name='book_trip'),

    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/destinations/', views.customer_destinations, name='customer_destinations'),
    path('customer/bookings/', views.my_bookings, name='my_bookings'),
]