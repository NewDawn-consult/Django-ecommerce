from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from . import models


class StockFilter(admin.SimpleListFilter):
    title = 'stock status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return [
            ('out', 'Out of Stock'),
            ('low', 'Low Stock (< 5)'),
            ('in', 'In Stock'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'out':
            return queryset.filter(stock=0)
        if self.value() == 'low':
            return queryset.filter(stock__gt=0, stock__lt=5)
        if self.value() == 'in':
            return queryset.filter(stock__gte=5)
        return queryset


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1
    fields = ['image', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; border-radius: 4px;" />',
                obj.image.url
            )
        return ''
    image_preview.short_description = 'Preview'


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = [
        'image_thumbnail', 'name', 'slug', 'product_count', 'description_short'
    ]
    list_display_links = ['name']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_per_page = 25
    fieldsets = [
        ('Category Information', {
            'fields': ['name', 'slug', 'description']
        }),
        ('Media', {
            'fields': ['image'],
            'classes': ['wide']
        }),
    ]

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 48px; height: 48px; object-fit: cover; '
                'border-radius: 6px;" />',
                obj.image.url
            )
        return format_html(
            '<span style="display: inline-flex; width: 48px; height: 48px; '
            'background: #f0f0f0; border-radius: 6px; align-items: center; '
            'justify-content: center; font-size: 20px;">📁</span>'
        )
    image_thumbnail.short_description = 'Image'

    def description_short(self, obj):
        return obj.description[:60] + '...' if obj.description and len(obj.description) > 60 else (obj.description or '-')
    description_short.short_description = 'Description'

    def product_count(self, obj):
        count = obj.products.count()
        url = f'/admin/store/product/?category__id__exact={obj.pk}'
        return format_html('<a href="{}">{}</a>', url, count)
    product_count.short_description = 'Products'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _product_count=Count('products')
        )


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = [
        'image_thumbnail', 'name', 'category', 'formatted_price',
        'stock_badge', 'featured', 'created_at'
    ]
    list_display_links = ['name']
    list_filter = [
        'featured', 'category', StockFilter, 'created_at'
    ]
    search_fields = ['name', 'description', 'category__name']
    list_editable = ['featured']
    list_per_page = 25
    date_hierarchy = 'created_at'
    inlines = [ProductImageInline]
    readonly_fields = ['created_at']
    save_on_top = True

    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'slug', 'category', 'description'],
        }),
        ('Pricing & Inventory', {
            'fields': ['price', 'stock', 'featured'],
            'classes': ['wide'],
        }),
        ('Media', {
            'fields': ['image'],
            'classes': ['wide'],
        }),
        ('Timestamps', {
            'fields': ['created_at'],
            'classes': ['collapse'],
        }),
    ]

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 48px; height: 48px; object-fit: cover; '
                'border-radius: 6px;" />',
                obj.image.url
            )
        return format_html(
            '<span style="display: inline-flex; width: 48px; height: 48px; '
            'background: #f0f0f0; border-radius: 6px; align-items: center; '
            'justify-content: center; font-size: 20px;">📦</span>'
        )
    image_thumbnail.short_description = 'Image'

    def formatted_price(self, obj):
        return format_html(
            '<span style="font-weight: 600;">${}</span>', obj.price
        )
    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price'

    def stock_badge(self, obj):
        if obj.stock == 0:
            return format_html(
                '<span style="background: #dc3545; color: #fff; padding: 2px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: 600;">Out</span>'
            )
        if obj.stock < 5:
            return format_html(
                '<span style="background: #ffc107; color: #000; padding: 2px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
                obj.stock
            )
        return format_html(
            '<span style="background: #198754; color: #fff; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            obj.stock
        )
    stock_badge.short_description = 'Stock'
    stock_badge.admin_order_field = 'stock'

@admin.register(models.ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product_link', 'user_link', 'rating_stars', 'comment_short', 'created_at'
    ]
    list_filter = ['rating', 'created_at']
    search_fields = ['comment', 'user__username', 'user__email', 'product__name']
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

    fieldsets = [
        ('Review', {
            'fields': ['product', 'user', 'rating', 'comment'],
        }),
        ('Timestamps', {
            'fields': ['created_at'],
            'classes': ['collapse'],
        }),
    ]

    def product_link(self, obj):
        url = f'/admin/store/product/{obj.product.pk}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'

    def user_link(self, obj):
        url = f'/admin/auth/user/{obj.user.pk}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = '#198754' if obj.rating >= 4 else '#ffc107' if obj.rating >= 3 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-size: 14px; letter-spacing: 1px;">{}</span>',
            color, stars
        )
    rating_stars.short_description = 'Rating'
    rating_stars.admin_order_field = 'rating'

    def comment_short(self, obj):
        return obj.comment[:80] + '...' if len(obj.comment) > 80 else obj.comment
    comment_short.short_description = 'Comment'


@admin.register(models.Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'product__name']
    date_hierarchy = 'created_at'
