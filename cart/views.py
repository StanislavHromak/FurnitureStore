from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .services import add_to_cart, remove_from_cart, get_cart_items, get_cart_total

@login_required
def cart_detail(request):
    items = get_cart_items(request.user)
    total = get_cart_total(request.user)
    return render(request, 'cart/cart_detail.html', {'cart_items': items, 'total': total})

@login_required
def cart_add(request, product_id):
    add_to_cart(request.user, product_id)
    return redirect('cart:cart_detail')

@login_required
def cart_remove(request, product_id):
    remove_from_cart(request.user, product_id)
    return redirect('cart:cart_detail')

