from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from cart.services import get_cart_items, get_cart_total, clear_cart
from .models import Order, OrderItem

@login_required
def create_order(request):
    if request.method == 'POST':
        cart_items = get_cart_items(request.user)
        if not cart_items.exists():
            messages.error(request, "Ваш кошик порожній.")
            return redirect('cart:cart_detail')

        total = get_cart_total(request.user)
        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),  # Додаємо обробку адреси
            total_price=total,
            created_at=timezone.now()
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        clear_cart(request.user)
        messages.success(request, f"Замовлення #{order.id} успішно створено! Дякуємо за покупку.")
        return redirect('orders:order_history')

    cart_items = get_cart_items(request.user)
    total = get_cart_total(request.user)
    return render(request, 'orders/create_order.html', {'cart_items': cart_items, 'total': total})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})
