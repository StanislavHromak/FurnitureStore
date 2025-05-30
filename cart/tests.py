from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Product, Category
from .models import CartItem
from .services import add_to_cart, remove_from_cart, clear_cart, get_cart_items, get_cart_total
from django.core.files.base import ContentFile

# Ініціалізація тестового клієнта
client = Client()

class CartItemModelTest(TestCase):
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
        self.cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )

    def test_cart_item_creation(self):
        """Перевірка створення об'єкта CartItem."""
        self.assertEqual(str(self.cart_item), '2 x Test Product for testuser')
        self.assertEqual(self.cart_item.total_price(), 200)  # 2 * 100
        self.assertEqual(self.cart_item.user, self.user)
        self.assertEqual(self.cart_item.product, self.product)
        self.assertEqual(self.cart_item.quantity, 2)

    def test_default_quantity(self):
        """Перевірка значення за замовчування для quantity."""
        new_item = CartItem.objects.create(user=self.user, product=self.product)
        self.assertEqual(new_item.quantity, 1)

class CartServicesTest(TestCase):
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
        self.product2 = Product.objects.create(
            name='Test Product 2',
            slug='test-product-2',
            category=self.category,
            price=150.00,
            description='Description 2',
            quantity=3,
            image=test_image
        )

    def test_add_to_cart_success(self):
        """Перевірка додавання товару до кошика."""
        add_to_cart(self.user, self.product.id)
        self.product.refresh_from_db()
        cart_items = get_cart_items(self.user)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 1)
        self.assertEqual(self.product.quantity, 4)  # Зменшено на 1

    def test_add_to_cart_existing_item(self):
        """Перевірка додавання товару, якщо він уже в кошику."""
        CartItem.objects.create(user=self.user, product=self.product, quantity=1)
        initial_quantity = self.product.quantity
        add_to_cart(self.user, self.product.id)
        self.product.refresh_from_db()
        cart_items = get_cart_items(self.user)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 2)
        self.assertEqual(self.product.quantity, initial_quantity - 1)  # Зменшено на 1

    def test_add_to_cart_out_of_stock(self):
        """Перевірка помилки при додаванні товару, якого немає на складі."""
        self.product.quantity = 0
        self.product.save()
        with self.assertRaises(ValueError) as context:
            add_to_cart(self.user, self.product.id)
        self.assertEqual(str(context.exception), "Товар відсутній на складі.")

    def test_remove_from_cart(self):
        """Перевірка видалення товару з кошика."""
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        self.product.quantity -= 2  # Синхронізуємо кількість товару
        self.product.save()
        initial_quantity = self.product.quantity
        remove_from_cart(self.user, self.product.id)
        self.product.refresh_from_db()
        self.assertEqual(get_cart_items(self.user).count(), 0)
        self.assertEqual(self.product.quantity, initial_quantity + 2)  # Повертаємо кількість

    def test_clear_cart(self):
        """Перевірка очищення кошика."""
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        CartItem.objects.create(user=self.user, product=self.product2, quantity=1)
        clear_cart(self.user)
        self.assertEqual(get_cart_items(self.user).count(), 0)

    def test_get_cart_items(self):
        """Перевірка отримання товарів з кошика."""
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        CartItem.objects.create(user=self.user, product=self.product2, quantity=1)
        items = get_cart_items(self.user)
        self.assertEqual(items.count(), 2)

    def test_get_cart_total(self):
        """Перевірка обчислення загальної суми кошика."""
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)  # 2 * 100 = 200
        CartItem.objects.create(user=self.user, product=self.product2, quantity=1)  # 1 * 150 = 150
        total = get_cart_total(self.user)
        self.assertEqual(total, 350)

    def test_get_cart_total_empty(self):
        """Перевірка обчислення загальної суми для порожнього кошика."""
        total = get_cart_total(self.user)
        self.assertEqual(total, 0)

class CartViewsTest(TestCase):
    def setUp(self):
        """Створюємо тестові об'єкти перед кожним тестом."""
        CustomUser = get_user_model()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.cart_detail_url = reverse('cart:cart_detail')

    def tearDown(self):
        """Очищаємо кошик після кожного тесту."""
        CartItem.objects.all().delete()

    def _create_product(self):
        """Допоміжний метод для створення продукту."""
        test_image = ContentFile(b"dummy image data", name="test_image.jpg")
        product = Product.objects.create(
            name='Test Product',
            slug='test-product-' + str(Product.objects.count() + 1),
            category=self.category,
            price=100.00,
            description='Description',
            quantity=5,
            image=test_image
        )
        return product

    def test_cart_urls(self):
        """Перевірка правильності маршрутів."""
        product = self._create_product()
        self.assertEqual(reverse('cart:cart_detail'), '/cart/')
        self.assertEqual(reverse('cart:cart_add', kwargs={'product_id': product.id}), f'/cart/add/{product.id}/')
        self.assertEqual(reverse('cart:cart_remove', kwargs={'product_id': product.id}), f'/cart/remove/{product.id}/')

    def test_cart_detail_view_get(self):
        """Перевірка GET-запиту на сторінку кошика."""
        client.login(username='testuser', password='testpass123')
        response = client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_detail.html')

    def test_cart_detail_view_unauthenticated(self):
        """Перевірка доступу до сторінки кошика без авторизації."""
        response = client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, 302)  # Перенаправлення на логін

    def test_cart_add_view_success(self):
        """Перевірка GET-запиту на додавання товару."""
        product = self._create_product()
        print(f"Before adding to cart: product.quantity = {product.quantity}")
        cart_add_url = reverse('cart:cart_add', kwargs={'product_id': product.id})
        client.login(username='testuser', password='testpass123')
        response = client.get(cart_add_url)
        self.assertEqual(response.status_code, 302)  # Перенаправлення на cart_detail
        self.assertEqual(CartItem.objects.count(), 1)
        product.refresh_from_db()
        self.assertEqual(product.quantity, 4)

    def test_cart_add_view_out_of_stock(self):
        """Перевірка помилки при додаванні товару, якого немає на складі."""
        product = self._create_product()
        cart_add_url = reverse('cart:cart_add', kwargs={'product_id': product.id})
        client.login(username='testuser', password='testpass123')
        product.quantity = 0
        product.save()
        response = client.get(cart_add_url)
        self.assertEqual(response.status_code, 302)  # Перенаправлення на cart_detail
        self.assertEqual(CartItem.objects.count(), 0)

    def test_cart_remove_view_success(self):
        """Перевірка видалення товару з кошика."""
        product = self._create_product()
        print(f"Before creating cart item: product.quantity = {product.quantity}")
        cart_remove_url = reverse('cart:cart_remove', kwargs={'product_id': product.id})
        client.login(username='testuser', password='testpass123')
        CartItem.objects.create(user=self.user, product=product, quantity=2)
        product.quantity -= 2  # Синхронізуємо кількість
        product.save()
        print(f"Before removing from cart: product.quantity = {product.quantity}")
        initial_quantity = product.quantity
        response = client.get(cart_remove_url)
        self.assertEqual(response.status_code, 302)  # Перенаправлення на cart_detail
        self.assertEqual(CartItem.objects.count(), 0)
        product.refresh_from_db()
        self.assertEqual(product.quantity, initial_quantity + 2)