from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'price', 'quantity', 'total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'shipping_name', 'email', 'total',
        'status', 'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['shipping_name', 'email', 'id']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['subtotal', 'tax', 'total', 'created_at', 'updated_at']
    fieldsets = [
        ('Customer', {
            'fields': ['user', 'shipping_name', 'phone', 'email'],
        }),
        ('Shipping', {
            'fields': ['address', 'city', 'region', 'order_notes'],
        }),
        ('Totals', {
            'fields': ['subtotal', 'tax', 'total'],
        }),
        ('Status', {
            'fields': ['status', 'created_at', 'updated_at'],
        }),
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'price', 'quantity', 'total_price']
    list_filter = ['order']
