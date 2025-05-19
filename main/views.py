from django.shortcuts import render
from catalog.models import Product

def chunked(iterable, size):
    return [iterable[i:i + size] for i in range(0, len(iterable), size)]

def home(request):
    all_products = Product.objects.filter(is_featured=True)
    chunked_products = chunked(all_products, 3)  # Групуємо по 3 товари
    return render(request, 'main/index.html', {'chunked_products': chunked_products})

def about(request):
    return render(request, 'main/about.html')

def design(request):
    products = Product.objects.all()[:6]
    return render(request, 'main/design.html', {'products': products})

def shop(request):
    products = Product.objects.all()  # Усі товари для магазину
    return render(request, 'main/shop.html', {'products': products})

