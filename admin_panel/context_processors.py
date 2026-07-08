from django.contrib.auth import get_user_model

User = get_user_model()


def admin_permissions(request):
    user = request.user
    return {
        'can': {
            'manage_categories': user.has_perm('store.change_category'),
            'add_category': user.has_perm('store.add_category'),
            'delete_category': user.has_perm('store.delete_category'),
            'manage_products': user.has_perm('store.change_product'),
            'add_product': user.has_perm('store.add_product'),
            'delete_product': user.has_perm('store.delete_product'),
            'manage_orders': user.has_perm('orders.change_order'),
            'manage_users': user.has_perm('auth.change_user'),
            'add_user': user.has_perm('auth.add_user'),
            'delete_user': user.has_perm('auth.delete_user'),
            'manage_groups': user.has_perm('auth.change_group'),
            'add_group': user.has_perm('auth.add_group'),
            'delete_group': user.has_perm('auth.delete_group'),
            'view_customers': user.is_staff,
            'view_subscribers': user.is_staff,
            'view_reports': user.is_staff,
        }
    }
