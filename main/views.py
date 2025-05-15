from django.shortcuts import render
from catalog.models import Product

def home(request):
    featured_products = Product.objects.filter(is_featured=True)[:4]
    return render(request, 'main/index.html', {'featured_products': featured_products})

def about(request):
    return render(request, 'main/about.html')

def design(request):
    products = Product.objects.all()[:6]
    return render(request, 'main/design.html', {'products': products})

def shop(request):
    products = Product.objects.all()  # Усі товари для магазину
    return render(request, 'main/shop.html', {'products': products})

def contact(request):
    return render(request, 'main/contact.html')

