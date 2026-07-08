from decimal import Decimal
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout as auth_logout
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from django.contrib import messages
from store.models import Product, Category
from orders.models import Order, OrderItem
from core.models import Newsletter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .forms import ProductForm, ProductImageFormSet, UserCreateForm, UserEditForm, GroupForm, CategoryForm


User = get_user_model()


def admin_logout(request):
    auth_logout(request)
    return redirect('admin_panel:login')


class AdminLoginView(LoginView):
    template_name = 'admin_panel/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return redirect('admin_panel:dashboard').url


@staff_member_required(login_url='admin_panel:login')
def dashboard(request):
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    customer_count = User.objects.filter(is_staff=False).count()
    revenue = Order.objects.aggregate(total=Sum('total'))['total'] or Decimal('0')

    out_of_stock_count = Product.objects.filter(stock=0).count()
    recent_orders = Order.objects.select_related('user').all()[:5]
    low_stock = Product.objects.filter(stock__gt=0, stock__lt=5)[:5]
    recent_products = Product.objects.select_related('category').all()[:5]
    recent_customers = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]

    orders_by_status_qs = Order.objects.values('status').annotate(count=Count('id'))
    status_counts = {item['status']: item['count'] for item in orders_by_status_qs}
    orders_by_status = [
        {'status': status, 'count': status_counts.get(status, 0)}
        for status, _ in Order.STATUS_CHOICES
    ]
    products_by_category = Category.objects.annotate(count=Count('products')).values('name', 'count')

    context = {
        'section': 'dashboard',
        'product_count': product_count,
        'order_count': order_count,
        'customer_count': customer_count,
        'revenue': revenue,
        'out_of_stock_count': out_of_stock_count,
        'recent_orders': recent_orders,
        'low_stock': low_stock,
        'recent_products': recent_products,
        'recent_customers': recent_customers,
        'orders_by_status': list(orders_by_status),
        'products_by_category': list(products_by_category),
    }
    return render(request, 'admin_panel/dashboard.html', context)


@staff_member_required(login_url='admin_panel:login')
def product_list(request):
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')
    featured_filter = request.GET.get('featured', '')

    products = Product.objects.select_related('category').all()
    if q:
        products = products.filter(name__icontains=q)
    if category_id:
        products = products.filter(category_id=category_id)
    if stock_filter == 'in':
        products = products.filter(stock__gt=5)
    elif stock_filter == 'low':
        products = products.filter(stock__gte=1, stock__lte=5)
    elif stock_filter == 'out':
        products = products.filter(stock=0)
    if featured_filter == 'yes':
        products = products.filter(featured=True)
    elif featured_filter == 'no':
        products = products.filter(featured=False)

    out_of_stock = products.filter(stock=0)
    categories = Category.objects.all()
    return render(request, 'admin_panel/product_list.html', {
        'section': 'products',
        'products': products,
        'out_of_stock': out_of_stock,
        'categories': categories,
        'q': q,
        'selected_category': category_id,
        'selected_stock': stock_filter,
        'selected_featured': featured_filter,
    })


@staff_member_required(login_url='admin_panel:login')
def order_list(request):
    orders = Order.objects.select_related('user').all()
    return render(request, 'admin_panel/order_list.html', {'section': 'orders', 'orders': orders})


@staff_member_required(login_url='admin_panel:login')
def order_update_status(request, pk):
    if not request.user.has_perm('orders.change_order'):
        raise PermissionDenied
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.pk} marked as {order.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('admin_panel:order_list')


@staff_member_required(login_url='admin_panel:login')
def customer_list(request):
    customers = User.objects.filter(is_staff=False).order_by('-date_joined')
    return render(request, 'admin_panel/customer_list.html', {'section': 'customers', 'customers': customers})


@staff_member_required(login_url='admin_panel:login')
def reports(request):
    today = timezone.now().date()

    monthly_sales = (
        Order.objects.filter(status__in=['completed', 'processing'])
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )

    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_orders = (
        Order.objects.filter(created_at__gte=thirty_days_ago)
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    top_products = (
        OrderItem.objects.values('product_name')
        .annotate(total_qty=Sum('quantity'), total_revenue=Sum('price'))
        .order_by('-total_qty')[:10]
    )

    customer_growth = (
        User.objects.filter(is_staff=False)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    context = {
        'section': 'reports',
        'monthly_sales': list(monthly_sales),
        'daily_orders': list(daily_orders),
        'top_products': list(top_products),
        'customer_growth': list(customer_growth),
    }
    return render(request, 'admin_panel/reports.html', context)


@staff_member_required(login_url='admin_panel:login')
def user_list(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        is_staff = request.POST.get('is_staff') == '1'
        target_user = get_object_or_404(User, pk=user_id)
        if target_user == request.user:
            messages.error(request, 'You cannot change your own staff status.')
        else:
            target_user.is_staff = is_staff
            target_user.save()
            messages.success(request, f'{target_user.username} staff status updated.')
        return redirect('admin_panel:user_list')

    users = User.objects.prefetch_related('groups').filter(is_superuser=True) | User.objects.filter(is_staff=True, is_superuser=False).prefetch_related('groups')
    users = users.order_by('-is_superuser', '-date_joined')
    return render(request, 'admin_panel/user_list.html', {
        'section': 'users',
        'users': users,
    })


@staff_member_required(login_url='admin_panel:login')
def user_add(request):
    if not request.user.has_perm('auth.add_user'):
        raise PermissionDenied
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" created successfully.')
            return redirect('admin_panel:user_list')
    else:
        form = UserCreateForm()
    return render(request, 'admin_panel/user_form.html', {
        'section': 'users',
        'form': form,
        'title': 'Add User',
    })


@staff_member_required(login_url='admin_panel:login')
def user_edit(request, pk):
    if not request.user.has_perm('auth.change_user'):
        raise PermissionDenied
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" updated.')
            return redirect('admin_panel:user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'admin_panel/user_form.html', {
        'section': 'users',
        'form': form,
        'title': 'Edit User',
        'user_obj': user,
    })


@staff_member_required(login_url='admin_panel:login')
def user_delete(request, pk):
    if not request.user.has_perm('auth.delete_user'):
        raise PermissionDenied
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('admin_panel:user_list')
    if request.method == 'POST':
        name = user.username
        user.delete()
        messages.success(request, f'User "{name}" deleted.')
        return redirect('admin_panel:user_list')
    return render(request, 'admin_panel/user_confirm_delete.html', {
        'section': 'users',
        'user_obj': user,
    })


@staff_member_required(login_url='admin_panel:login')
def group_list(request):
    groups = Group.objects.annotate(user_count=Count('user')).all()
    return render(request, 'admin_panel/group_list.html', {
        'section': 'groups',
        'groups': groups,
    })


@staff_member_required(login_url='admin_panel:login')
def group_add(request):
    if not request.user.has_perm('auth.add_group'):
        raise PermissionDenied
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group created successfully.')
            return redirect('admin_panel:group_list')
    else:
        form = GroupForm()
    return render(request, 'admin_panel/group_form.html', {
        'section': 'groups',
        'form': form,
        'title': 'Add Group',
    })


@staff_member_required(login_url='admin_panel:login')
def group_edit(request, pk):
    if not request.user.has_perm('auth.change_group'):
        raise PermissionDenied
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f'Group "{group.name}" updated.')
            return redirect('admin_panel:group_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'admin_panel/group_form.html', {
        'section': 'groups',
        'form': form,
        'title': 'Edit Group',
    })


@staff_member_required(login_url='admin_panel:login')
def group_delete(request, pk):
    if not request.user.has_perm('auth.delete_group'):
        raise PermissionDenied
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        name = group.name
        group.delete()
        messages.success(request, f'Group "{name}" deleted.')
        return redirect('admin_panel:group_list')
    return render(request, 'admin_panel/group_confirm_delete.html', {
        'section': 'groups',
        'group': group,
    })


@staff_member_required(login_url='admin_panel:login')
def subscriber_list(request):
    subscribers = Newsletter.objects.all()
    return render(request, 'admin_panel/subscriber_list.html', {
        'section': 'subscribers',
        'subscribers': subscribers,
    })


@staff_member_required(login_url='admin_panel:login')
def product_create(request):
    if not request.user.has_perm('store.add_product'):
        raise PermissionDenied
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('admin_panel:product_list')
    else:
        form = ProductForm()
        formset = ProductImageFormSet()
    return render(request, 'admin_panel/product_form.html', {
        'section': 'products',
        'form': form,
        'formset': formset,
        'title': 'Add Product',
    })


@staff_member_required(login_url='admin_panel:login')
def product_update(request, pk):
    if not request.user.has_perm('store.change_product'):
        raise PermissionDenied
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('admin_panel:product_list')
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)
    return render(request, 'admin_panel/product_form.html', {
        'section': 'products',
        'form': form,
        'formset': formset,
        'title': 'Edit Product',
        'product': product,
    })


@staff_member_required(login_url='admin_panel:login')
def product_delete(request, pk):
    if not request.user.has_perm('store.delete_product'):
        raise PermissionDenied
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
        return redirect('admin_panel:product_list')
    return render(request, 'admin_panel/product_confirm_delete.html', {
        'section': 'products',
        'product': product,
    })


@staff_member_required(login_url='admin_panel:login')
def category_list(request):
    q = request.GET.get('q', '').strip()
    categories = Category.objects.annotate(product_count=Count('products')).all()
    if q:
        categories = categories.filter(name__icontains=q)
    return render(request, 'admin_panel/category_list.html', {
        'section': 'categories',
        'categories': categories,
        'q': q,
    })


@staff_member_required(login_url='admin_panel:login')
def category_add(request):
    if not request.user.has_perm('store.add_category'):
        raise PermissionDenied
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('admin_panel:category_list')
    else:
        form = CategoryForm()
    return render(request, 'admin_panel/category_form.html', {
        'section': 'categories',
        'form': form,
        'title': 'Add Category',
    })


@staff_member_required(login_url='admin_panel:login')
def category_edit(request, pk):
    if not request.user.has_perm('store.change_category'):
        raise PermissionDenied
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated.')
            return redirect('admin_panel:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_panel/category_form.html', {
        'section': 'categories',
        'form': form,
        'title': 'Edit Category',
        'category': category,
    })


@staff_member_required(login_url='admin_panel:login')
def category_delete(request, pk):
    if not request.user.has_perm('store.delete_category'):
        raise PermissionDenied
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted.')
        return redirect('admin_panel:category_list')
    return render(request, 'admin_panel/category_confirm_delete.html', {
        'section': 'categories',
        'category': category,
    })
