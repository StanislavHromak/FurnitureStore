from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # Фільтрація за категорією
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Пошук за назвою
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(Q(name__icontains=search_query))

    return render(request, 'catalog/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query
    })


def category_products(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'catalog/product_list.html', {
        'category': category,
        'products': products,
        'categories': categories
    })


def product_detail(request, product_id):  # Змінюємо параметр на product_id
    product = get_object_or_404(Product, id=product_id)  # Використовуємо id замість slug
    return render(request, 'catalog/product_detail.html', {
        'product': product
    })


def featured_products(request):
    products = Product.objects.filter(is_featured=True)[:6]
    return render(request, 'catalog/featured_products.html', {
        'products': products
    })
