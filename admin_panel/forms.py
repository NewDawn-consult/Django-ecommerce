from django import forms
from django.forms import inlineformset_factory
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group, Permission
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Submit, HTML, Div
from store.models import Product, ProductImage, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'featured', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-8'),
                Column('category', css_class='col-md-4'),
                css_class='g-3',
            ),
            'description',
            Row(
                Column('price', css_class='col-md-4'),
                Column('stock', css_class='col-md-4'),
                Column(
                    Field('featured', css_class='form-check-input'),
                    css_class='col-md-4 d-flex align-items-end pb-3',
                ),
                css_class='g-3',
            ),
            'image',
        )


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']


ProductImageFormSet = inlineformset_factory(
    Product, ProductImage, form=ProductImageForm,
    extra=3, can_delete=True, max_num=10,
)


class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'}))
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
        self.fields['password1'].help_text = 'At least 8 characters. Not too common or entirely numeric.'

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            'username',
            'email',
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
                css_class='g-3',
            ),
            'password1',
            'password2',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('groups', is_stacked=False),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'password1', 'password2', 'groups']

    class Media:
        css = {'all': ['admin/css/widgets.css']}
        js = ['admin/js/core.js', 'admin/js/SelectBox.js', 'admin/js/SelectFilter2.js']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'At least 8 characters.'
        if self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
                css_class='g-3',
            ),
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
                css_class='g-3',
            ),
            Row(
                Column('is_staff', css_class='col-md-6'),
                Column('is_superuser', css_class='col-md-6'),
                css_class='g-3',
            ),
            Row(
                Column('password1', css_class='col-md-6'),
                Column('password2', css_class='col-md-6'),
                css_class='g-3',
            ),
            Field('groups', css_class='vTextField'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        if user.pk:
            user.groups.set(self.cleaned_data['groups'])
        return user


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    password = forms.CharField(
        label='New Password (leave blank to keep current)',
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current'}),
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('groups', is_stacked=False),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'groups']

    class Media:
        css = {'all': ['admin/css/widgets.css']}
        js = ['admin/js/core.js', 'admin/js/SelectBox.js', 'admin/js/SelectFilter2.js']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
                css_class='g-3',
            ),
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
                css_class='g-3',
            ),
            Row(
                Column('is_staff', css_class='col-md-6'),
                Column('is_superuser', css_class='col-md-6'),
                css_class='g-3',
            ),
            'password',
            Field('groups', css_class='vTextField'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        if user.pk:
            user.groups.set(self.cleaned_data['groups'])
        return user


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related('content_type').all(),
        required=False,
        widget=FilteredSelectMultiple('permissions', is_stacked=False),
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

    class Media:
        css = {'all': ['admin/css/widgets.css']}
        js = ['admin/js/core.js', 'admin/js/SelectBox.js', 'admin/js/SelectFilter2.js']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['permissions'].initial = self.instance.permissions.all()
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            'name',
            Field('permissions', css_class='vTextField'),
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('icon', css_class='col-md-6'),
                css_class='g-3 mb-3',
            ),
            'description',
            'image',
        )
