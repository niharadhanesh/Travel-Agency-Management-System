from django.conf import settings
from django.db import models
from django.utils.text import slugify

from .destination_data import INCLUDED


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



def _inr(n):
    """25000 -> '25,000', 120000 -> '1,20,000' (Indian digit grouping)."""
    s = str(int(n))
    if len(s) <= 3:
        return s
    head, tail, parts = s[:-3], s[-3:], []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ','.join(parts + [tail])


def _lines(text):
    """One 'Title | description' per line -> list of (title, description)."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        title, _, desc = line.partition('|')
        rows.append((title.strip(), desc.strip()))
    return rows


class Destination(models.Model):
    REGION_CHOICES = [
        ('India', 'India'),
        ('Asia', 'Asia'),
        ('Middle East', 'Middle East'),
        ('Islands', 'Islands'),
        ('Europe', 'Europe'),
    ]
    ICONS = ['geo-alt', 'stars', 'camera', 'heart', 'compass', 'sun']

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    tagline = models.CharField(max_length=200)
    overview = models.TextField()
    best_time = models.CharField(max_length=60, help_text='e.g. Sep - Mar')
    duration = models.CharField(max_length=60, help_text='e.g. 5 Days / 4 Nights')
    price = models.PositiveIntegerField(help_text='Starting price per person in INR')
    language = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=60, blank=True)
    image = models.ImageField(upload_to='destinations/', blank=True)
    image_url = models.URLField(blank=True)
    highlights = models.TextField(blank=True, help_text='One per line: Title | short description')
    itinerary = models.TextField(blank=True, help_text='One day per line: Title | what happens')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'destination'
            slug, n = base, 2
            while Destination.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def image_src(self):
        return self.image.url if self.image else self.image_url

    @property
    def price_display(self):
        return _inr(self.price)

    def as_dict(self):
        """Same shape as the built-in entries in destination_data.DESTINATIONS."""
        return {
            'slug': self.slug,
            'name': self.name,
            'country': self.country,
            'region': self.region,
            'tagline': self.tagline,
            'overview': self.overview,
            'best_time': self.best_time,
            'duration': self.duration,
            'price': _inr(self.price),
            'language': self.language or '-',
            'currency': self.currency or '-',
            'highlights': [(self.ICONS[i % len(self.ICONS)], t, d) for i, (t, d) in enumerate(_lines(self.highlights))],
            'itinerary': _lines(self.itinerary),
            'included': INCLUDED,
            'image': self.image_src,
            'thumb': self.image_src,
        }

    def __str__(self):
        return f'{self.name}, {self.country}'