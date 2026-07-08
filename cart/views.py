from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from store.models import Product
from .cart import (
    add_to_cart, remove_from_cart, update_cart,
    get_cart_items, get_cart_count, clear_cart,
)


def cart_detail(request):
    if request.method == 'POST':
        clear_cart(request)
        messages.success(request, 'Cart cleared.')
        return redirect('cart:cart_detail')

    items = get_cart_items(request)
    subtotal = sum(item['total_price'] for item in items)
    tax = subtotal * Decimal('0.08')
    total = subtotal + tax
    context = {
        'cart_items': items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'cart/cart_detail.html', context)


def cart_add(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        if quantity > product.stock:
            messages.error(request, 'Not enough stock available.')
            return redirect('store:product_detail', pk=product_id)
        add_to_cart(request, product_id, quantity)
        messages.success(request, f'"{product.name}" added to your cart.')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


def cart_remove(request, item_id):
    if request.method == 'POST':
        remove_from_cart(request, item_id)
        messages.success(request, 'Item removed from cart.')
    return redirect('cart:cart_detail')


def cart_update(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        update_cart(request, item_id, quantity)
        messages.success(request, 'Cart updated.')
    return redirect('cart:cart_detail')
