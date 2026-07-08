from django import forms


class CheckoutForm(forms.Form):
    shipping_name = forms.CharField(
        max_length=200, label='Full Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
    )
    phone = forms.CharField(
        max_length=20, label='Phone',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+233 50 000 0000'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john@example.com'}),
    )
    address = forms.CharField(
        label='Address',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '123 Main St'}),
    )
    city = forms.CharField(
        max_length=100, label='City',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Accra'}),
    )
    region = forms.CharField(
        max_length=100, label='Region',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Greater Accra'}),
    )
    order_notes = forms.CharField(
        required=False, label='Order Notes (optional)',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special instructions...'}),
    )
