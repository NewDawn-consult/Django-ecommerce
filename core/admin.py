from django.contrib import admin
from .models import ContactMessage, Newsletter


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = [
        ('Sender', {
            'fields': ['name', 'email'],
        }),
        ('Message', {
            'fields': ['subject', 'message'],
        }),
        ('Status', {
            'fields': ['is_read', 'created_at'],
        }),
    ]


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    actions = ['deactivate_subscribers', 'activate_subscribers']

    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} subscriber(s) deactivated.')
    deactivate_subscribers.short_description = 'Deactivate selected subscribers'

    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} subscriber(s) activated.')
    activate_subscribers.short_description = 'Activate selected subscribers'
