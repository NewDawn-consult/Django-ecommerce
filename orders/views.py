from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.cart import get_cart_items, get_cart_count, clear_cart
from .models import Order, OrderItem
from .forms import CheckoutForm


def checkout(request):
    cart_items = get_cart_items(request)
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    subtotal = sum(item['total_price'] for item in cart_items)
    tax = subtotal * Decimal('0.08')
    total = subtotal + tax

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            in_stock = True
            for item in cart_items:
                if item['quantity'] > item['product'].stock:
                    in_stock = False
                    messages.error(
                        request,
                        f'"{item["product"].name}" only has {item["product"].stock} in stock. '
                        f'Please update your cart.',
                    )

            if not in_stock:
                return redirect('cart:cart_detail')

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                shipping_name=cd['shipping_name'],
                phone=cd['phone'],
                email=cd['email'],
                address=cd['address'],
                city=cd['city'],
                region=cd['region'],
                order_notes=cd['order_notes'],
                subtotal=subtotal,
                tax=tax,
                total=total,
            )

            for item in cart_items:
                product = item['product']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=item['quantity'],
                )
                product.stock -= item['quantity']
                product.save(update_fields=['stock'])

            clear_cart(request)
            request.session['order_placed'] = order.pk
            messages.success(request, 'Order placed successfully!')
            return redirect('orders:order_confirmation', order_pk=order.pk)
    else:
        form = CheckoutForm(
            initial={
                'shipping_name': request.user.get_full_name() if request.user.is_authenticated else '',
                'email': request.user.email if request.user.is_authenticated else '',
            }
        )

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'orders/checkout.html', context)


def order_confirmation(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    return render(request, 'orders/order_confirmation.html', {'order': order})


def order_list(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to view your orders.')
        return redirect('accounts:login')

    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


def order_detail(request, order_pk):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, pk=order_pk, user=request.user)
    else:
        order = get_object_or_404(Order, pk=order_pk)

    status_choices = Order.STATUS_CHOICES
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'status_choices': status_choices,
    })


def order_invoice(request, order_pk):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, pk=order_pk, user=request.user)
    else:
        order = get_object_or_404(Order, pk=order_pk)

    return render(request, 'orders/invoice.html', {'order': order})
