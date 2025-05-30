from catalog.models import Product
from .models import CartItem

def add_to_cart(user, product_id, quantity=1):
    product = Product.objects.get(id=product_id)
    if product.quantity < quantity:
        raise ValueError("Товар відсутній на складі.")
    cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    product.quantity -= quantity
    product.save()
    print(f"After: product.quantity = {product.quantity}")

def remove_from_cart(user, product_id):
    cart_item = CartItem.objects.filter(user=user, product_id=product_id).first()
    if cart_item:
        product = cart_item.product
        print(f"Before remove: product.quantity = {product.quantity}, adding back = {cart_item.quantity}")
        product.quantity += cart_item.quantity
        product.save()
        print(f"After remove: product.quantity = {product.quantity}")
        cart_item.delete()

def clear_cart(user):
    CartItem.objects.filter(user=user).delete()

def get_cart_items(user):
    return CartItem.objects.filter(user=user)

def get_cart_total(user):
    items = get_cart_items(user)
    return sum(item.total_price() for item in items) if items.exists() else 0
