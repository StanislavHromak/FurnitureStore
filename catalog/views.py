from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'catalog/product_list.html', {
        'products': products,
        'categories': categories
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

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'catalog/product_detail.html', {
        'product': product
    })

def featured_products(request):
    products = Product.objects.filter(is_featured=True)[:6]  # Для design.html або index.html
    return render(request, 'catalog/featured_products.html', {
        'products': products
    })
