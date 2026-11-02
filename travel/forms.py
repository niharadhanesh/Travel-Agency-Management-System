from django import forms
from django.utils.text import slugify

from .destination_data import DESTINATIONS
from .models import Destination


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = [
            'name', 'country', 'region', 'tagline', 'overview',
            'best_time', 'duration', 'price', 'language', 'currency',
            'image', 'image_url', 'highlights', 'itinerary',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Santorini'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Greece'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'One line that sells the place'}),
            'overview': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'A short paragraph about the destination'}),
            'best_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apr - Oct'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5 Days / 4 Nights'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '45000', 'min': 1}),
            'language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Greek, English'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Euro (EUR)'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'highlights': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Sunset at Oia | Watch the sun go down over the caldera\nBlack sand beaches | Relax at Perissa'}),
            'itinerary': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Arrive in Fira | Hotel check-in and old town walk\nBoat tour | Volcano and hot springs'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        slug = slugify(name)
        if not slug:
            raise forms.ValidationError('Enter a valid destination name.')
        if slug in DESTINATIONS or Destination.objects.filter(slug=slug).exists():
            raise forms.ValidationError('A destination with this name already exists.')
        return name

    def clean(self):
        data = super().clean()
        if not data.get('image') and not data.get('image_url'):
            self.add_error('image', 'Upload a photo or paste an image link.')
        return data