# forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'autocomplete': 'off', 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete': 'off', 'placeholder': 'Your Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'autocomplete': 'off', 'placeholder': 'Your Message'}))