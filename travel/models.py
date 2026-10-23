from django.conf import settings
from django.db import models


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    destination_slug = models.SlugField()
    destination_name = models.CharField(max_length=100)
    travel_date = models.DateField()
    travellers = models.PositiveSmallIntegerField(default=1)
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def reference(self):
        return f'WB{self.pk + 1000}'

    def __str__(self):
        return f'{self.reference} - {self.destination_name} ({self.user})'