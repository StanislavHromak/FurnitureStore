from django.db import models
from django.conf import settings
from catalog.models import Product

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Користувач")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    first_name = models.CharField(max_length=50, verbose_name="Ім'я")
    last_name = models.CharField(max_length=50, verbose_name="Прізвище")
    email = models.EmailField(verbose_name="Електронна пошта")
    phone = models.CharField(max_length=15, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адреса доставки")  # Додаємо поле назад
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Загальна сума", default=0)

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f"Замовлення #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Замовлення")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Кількість")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")

    class Meta:
        verbose_name = "Елемент замовлення"
        verbose_name_plural = "Елементи замовлення"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
