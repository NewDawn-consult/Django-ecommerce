from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from .forms import ContactForm, NewsletterForm
from store.models import Product, Category


def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'You\'ve been subscribed! Check your inbox for a welcome offer.'
            )
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
    return redirect('core:home')


def home(request):
    featured_products = Product.objects.filter(featured=True).select_related('category')[:6]
    latest_products = Product.objects.all()[:8]
    categories = Category.objects.annotate(product_count=Count('products')).all()
    return render(request, 'core/home.html', {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'categories': categories,
    })


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Thank you! Your message has been received. We\'ll get back to you soon.'
            )
            return redirect('core:contact')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})
