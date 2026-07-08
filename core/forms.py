from django import forms
from .models import ContactMessage, Newsletter


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control border-end-0',
                'placeholder': 'Enter your email address',
                'aria-label': 'Email',
            }),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Your name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'your@email.com',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'How can we help?',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5,
                'placeholder': 'Tell us more about your inquiry...',
            }),
        }
