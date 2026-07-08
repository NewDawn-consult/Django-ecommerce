from decimal import Decimal
from django.conf import settings
from store.models import Product


CART_SESSION_KEY = 'cart'


def get_cart(request):
    return request.session.get(CART_SESSION_KEY, {})


def add_to_cart(request, product_id, quantity=1):
    cart = get_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        cart[product_id]['quantity'] += quantity
    else:
        cart[product_id] = {'quantity': quantity}
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def remove_from_cart(request, product_id):
    cart = get_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session[CART_SESSION_KEY] = cart
        request.session.modified = True


def update_cart(request, product_id, quantity):
    cart = get_cart(request)
    product_id = str(product_id)
    if quantity > 0 and product_id in cart:
        cart[product_id]['quantity'] = quantity
        request.session[CART_SESSION_KEY] = cart
        request.session.modified = True
    elif quantity <= 0:
        remove_from_cart(request, product_id)


def get_cart_items(request):
    cart = get_cart(request)
    if not cart:
        return []
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)
    products_dict = {str(p.id): p for p in products}
    items = []
    for pid, data in cart.items():
        product = products_dict.get(pid)
        if product is None:
            continue
        items.append({
            'product': product,
            'quantity': data['quantity'],
            'total_price': product.price * data['quantity'],
        })
    return items


def get_cart_subtotal(request):
    items = get_cart_items(request)
    return sum(item['total_price'] for item in items)


def get_cart_count(request):
    cart = get_cart(request)
    return sum(item['quantity'] for item in cart.values())


def clear_cart(request):
    if CART_SESSION_KEY in request.session:
        del request.session[CART_SESSION_KEY]
        request.session.modified = True
