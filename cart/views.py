from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from .services import add_to_cart, remove_from_cart, get_cart_items, get_cart_total

@login_required
def cart_detail(request):
    items = get_cart_items(request.user)
    total = get_cart_total(request.user)
    return render(request, 'cart/cart_detail.html', {'cart_items': items, 'total': total})

@login_required
def cart_add(request, product_id):
    try:
        add_to_cart(request.user, product_id)
        messages.success(request, "Товар успішно додано до кошика!")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('cart:cart_detail')

@login_required
def cart_remove(request, product_id):
    remove_from_cart(request.user, product_id)
    messages.success(request, "Товар видалено з кошика!")
    return redirect('cart:cart_detail')

