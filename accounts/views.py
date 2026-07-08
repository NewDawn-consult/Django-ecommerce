from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from store.models import Product, Wishlist
from .forms import UserRegistrationForm, UserUpdateForm
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Account created successfully! You can now log in.'
            )
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    recent_orders = request.user.orders.all()[:5]
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'recent_orders': recent_orders,
    })


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            avatar = form.cleaned_data.get('avatar')
            if avatar:
                profile.avatar = avatar
                profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def wishlist(request):
    items = request.user.wishlist.select_related('product__category').all()
    return render(request, 'accounts/wishlist.html', {'wishlist_items': items})


@login_required
@require_POST
def wishlist_toggle(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(
        user=request.user, product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        status = 'removed'
        messages.success(request, f'"{product.name}" removed from wishlist.')
    else:
        Wishlist.objects.create(user=request.user, product=product)
        status = 'added'
        messages.success(request, f'"{product.name}" added to wishlist.')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': status,
            'count': request.user.wishlist.count(),
        })

    return redirect(request.META.get('HTTP_REFERER', 'accounts:wishlist'))


@login_required
def dashboard(request):
    recent_orders = request.user.orders.all()[:5]
    wishlist_items = request.user.wishlist.select_related('product').all()
    order_count = request.user.orders.count()
    wishlist_count = wishlist_items.count()

    return render(request, 'accounts/dashboard.html', {
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
        'order_count': order_count,
        'wishlist_count': wishlist_count,
    })
