from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from .models import Product, Category, ProductReview
from .forms import ProductReviewForm


def category_list(request):
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).all()
    return render(request, 'store/category_list.html', {'categories': categories})


def product_list(request):
    products = Product.objects.select_related('category').all()

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    category_slug = request.GET.get('category', '').strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)

    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.annotate(
        product_count=Count('products')
    ).all()

    def _url(**overrides):
        params = request.GET.copy()
        for k, v in overrides.items():
            if v is None or v == '':
                if k in params:
                    del params[k]
            else:
                params[k] = str(v)
        qs = params.urlencode()
        return f'{request.path}?{qs}' if qs else request.path

    category_urls = {}
    for cat in categories:
        category_urls[cat.slug] = _url(category=cat.slug)
    clear_category_url = _url(category='')
    clear_search_url = _url(q='')
    clear_price_url = _url(min_price='', max_price='')
    clear_all_url = request.path

    sort_options = ['newest', 'price_asc', 'price_desc', 'name_asc', 'name_desc']
    sort_urls = {s: _url(sort=s, page='') for s in sort_options}

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_slug': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'base_url': request.path,
        'category_urls': category_urls,
        'clear_category_url': clear_category_url,
        'clear_search_url': clear_search_url,
        'clear_price_url': clear_price_url,
        'clear_all_url': clear_all_url,
        'sort_urls': sort_urls,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        slug=slug
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to submit a review.')
            return redirect('accounts:login')

        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            try:
                review.save()
                messages.success(request, 'Your review has been posted!')
            except Exception:
                messages.error(request, 'You have already reviewed this product.')
            return redirect('store:product_detail', slug=slug)
    else:
        form = ProductReviewForm()

    reviews = ProductReview.objects.filter(
        product=product
    ).select_related('user__profile')[:5]

    review_stats = ProductReview.objects.filter(product=product).aggregate(
        avg_rating=Avg('rating'),
        review_count=Count('id')
    )
    avg_rating = round(review_stats['avg_rating'] or 0, 1)
    review_count = review_stats['review_count'] or 0

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:4]

    if request.user.is_authenticated:
        is_in_wishlist = product.wishlisted_by.filter(user=request.user).exists()
        has_reviewed = ProductReview.objects.filter(user=request.user, product=product).exists()
    else:
        is_in_wishlist = False
        has_reviewed = False

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'related_products': related_products,
        'is_in_wishlist': is_in_wishlist,
        'has_reviewed': has_reviewed,
        'form': form,
    }
    return render(request, 'store/product_detail.html', context)
