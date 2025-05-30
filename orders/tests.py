from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from catalog.models import Product, Category
from cart.models import CartItem
from cart.services import clear_cart, add_to_cart, remove_from_cart
from .models import Order, OrderItem

# Ініціалізація тестового клієнта
client = Client()

class OrderModelTest(TestCase):
    def setUp(self):
        """Створюємо тестові об'єкти перед кожним тестом."""
        CustomUser = get_user_model()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        test_image = ContentFile(b"dummy image data", name="test_image.jpg")
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            price=100.00,
            description='Description',
            quantity=5,
            image=test_image
        )
        self.order = Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='123456789',
            address='Test Address',
            total_price=200.00,
            created_at=timezone.now()
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=100.00
        )

    def test_order_creation(self):
        """Перевірка створення об'єкта Order."""
        self.assertEqual(str(self.order), f"Замовлення #{self.order.id} - testuser")
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.first_name, 'John')
        self.assertEqual(self.order.total_price, 200.00)

    def test_order_item_creation(self):
        """Перевірка створення об'єкта OrderItem."""
        self.assertEqual(str(self.order_item), "2 x Test Product")
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, 100.00)

class OrderAdminTest(TestCase):
    def setUp(self):
        """Створюємо тестові об'єкти перед кожним тестом."""
        self.client = Client()
        CustomUser = get_user_model()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.superuser = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        test_image = ContentFile(b"dummy image data", name="test_image.jpg")
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            price=100.00,
            description='Description',
            quantity=5,
            image=test_image
        )
        self.order = Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='123456789',
            address='Test Address',
            total_price=200.00,
            created_at=timezone.now()
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=100.00
        )

    def test_order_admin_readonly(self):
        """Перевірка, що адмін-панель Order лише для читання."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/orders/order/{self.order.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'readonly')
        self.assertNotContains(response, 'add related')
        self.assertNotContains(response, 'delete selected')

    def test_order_admin_no_add(self):
        """Перевірка, що додавання замовлень у адмінці заборонено."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/orders/order/add/')
        self.assertEqual(response.status_code, 403)  # Заборонено для суперкористувача

    def test_order_item_inline_readonly(self):
        """Перевірка, що OrderItem у адмінці лише для читання."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/orders/order/{self.order.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'readonly')
        self.assertNotContains(response, 'add another OrderItem')

class OrderViewsTest(TestCase):
    def setUp(self):
        """Створюємо тестові об'єкти перед кожним тестом."""
        CustomUser = get_user_model()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        test_image = ContentFile(b"dummy image data", name="test_image.jpg")
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            price=100.00,
            description='Description',
            quantity=5,
            image=test_image
        )
        self.create_order_url = reverse('orders:create_order')
        self.order_history_url = reverse('orders:order_history')
        self.cart_detail_url = reverse('cart:cart_detail')

    def test_create_order_success(self):
        """Перевірка створення замовлення з кошика."""
        initial_quantity = self.product.quantity  # Початкова кількість = 5
        # Додаємо товар до кошика перед створенням замовлення
        add_to_cart(self.user, self.product.id)  # Зменшує quantity з 5 до 4
        client.login(username='testuser', password='testpass123')
        response = client.post(self.create_order_url, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '123456789',
            'address': 'Test Address'
        })
        self.assertEqual(response.status_code, 302)  # Перенаправлення на order_history
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(CartItem.objects.count(), 0)  # Кошик очищено
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, 100.00)  # 1 * 100 (оскільки quantity=1 після add_to_cart)
        self.assertEqual(order.items.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity - 1)  # Залишається 4 після add_to_cart, не змінюється при замовленні

    def test_create_order_empty_cart(self):
        """Перевірка створення замовлення з порожнім кошиком."""
        clear_cart(self.user)  # Очищаємо кошик
        client.login(username='testuser', password='testpass123')
        response = client.post(self.create_order_url, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '123456789',
            'address': 'Test Address'
        })
        self.assertEqual(response.status_code, 302)  # Перенаправлення на cart_detail
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_get(self):
        """Перевірка GET-запиту на створення замовлення."""
        client.login(username='testuser', password='testpass123')
        response = client.get(self.create_order_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/create_order.html')

    def test_order_history_view(self):
        """Перевірка перегляду історії замовлень."""
        Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='123456789',
            address='Test Address',
            total_price=200.00,
            created_at=timezone.now()
        )
        client.login(username='testuser', password='testpass123')
        response = client.get(self.order_history_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_history.html')
        self.assertContains(response, 'Test Address')  # Перевіряємо адресу
        self.assertContains(response, '200,00')  # Перевіряємо суму

    def test_order_history_unauthenticated(self):
        """Перевірка доступу до історії замовлень без авторизації."""
        response = client.get(self.order_history_url)
        self.assertEqual(response.status_code, 302)  # Перенаправлення на логін
