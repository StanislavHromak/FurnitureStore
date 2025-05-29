from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'catalog/product_detail.html', {'product': product})


def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')

    # Пошук
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    # Фільтр за категорією
    if category_id.isdigit():
        products = products.filter(category_id=int(category_id))

    # Фільтр за ціною
    if price_min.isdigit():
        products = products.filter(price__gte=price_min)
    if price_max.isdigit():
        products = products.filter(price__lte=price_max)

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': int(category_id) if category_id and category_id.isdigit() else '',
        'price_min': price_min,
        'price_max': price_max,
    }
    return render(request, 'main/shop.html', context)







