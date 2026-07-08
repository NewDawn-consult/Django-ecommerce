from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'date_joined'
    ]
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_per_page = 25
    date_hierarchy = 'date_joined'
    ordering = ['-date_joined']

    fieldsets = [
        ('Login Credentials', {
            'fields': ['username', 'password']
        }),
        ('Personal Information', {
            'fields': ['first_name', 'last_name', 'email']
        }),
        ('Permissions', {
            'fields': [
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ],
            'classes': ['wide'],
        }),
        ('Important Dates', {
            'fields': ['last_login', 'date_joined'],
            'classes': ['collapse'],
        }),
    ]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
