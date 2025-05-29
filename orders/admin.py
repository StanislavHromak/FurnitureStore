from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Забороняє додавання нових елементів
    readonly_fields = ('order', 'product', 'quantity', 'price')  # Усі поля лише для читання
    can_delete = False  # Забороняє видалення елементів
    show_change_link = False  # Приховує посилання на редагування

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price', 'first_name', 'last_name', 'email', 'phone', 'address')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'email', 'phone', 'first_name', 'last_name', 'address')
    inlines = [OrderItemInline]
    readonly_fields = ('user', 'created_at', 'total_price', 'first_name', 'last_name', 'email', 'phone', 'address')  # Усі поля лише для читання
    can_add = False  # Забороняє додавання нових замовлень
    can_delete = False  # Забороняє видалення замовлень
    can_change = False  # Забороняє редагування замовлень
    fieldsets = (
        (None, {'fields': ('user', 'created_at', 'total_price')}),
        ('Контактна інформація', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
