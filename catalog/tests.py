from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Category
from django.core.files.base import ContentFile

# Ініціалізація тестового клієнта
client = Client()

class CatalogViewsTest(TestCase):
    def setUp(self):
        """Створюємо тестові об'єкти перед кожним тестом."""
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        # Створюємо тестове зображення
        test_image = ContentFile(b"dummy image data", name="test_image.jpg")
        self.product1 = Product.objects.create(
            name='Product 1',
            slug='product-1',
            category=self.category,
            price=100.00,
            description='Description 1',
            is_featured=True,
            quantity=5,
            image=test_image  # Додаємо тестове зображення
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            slug='product-2',
            category=self.category,
            price=150.00,
            description='Description 2',
            is_featured=False,
            quantity=3,
            image=test_image  # Додаємо тестове зображення
        )

    def test_product_detail_view(self):
        """Перевірка GET-запиту на сторінку product_detail."""
        response = client.get(reverse('catalog:product_detail', kwargs={'product_id': self.product1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/product_detail.html')
        self.assertEqual(response.context['product'], self.product1)

    def test_product_detail_view_invalid_id(self):
        """Перевірка GET-запиту з неіснуючим product_id."""
        response = client.get(reverse('catalog:product_detail', kwargs={'product_id': 999}))
        self.assertEqual(response.status_code, 404)

    def test_shop_view_no_filters(self):
        """Перевірка GET-запиту на сторінку shop без фільтрів."""
        response = client.get(reverse('catalog:shop'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/shop.html')
        self.assertEqual(list(response.context['products']), [self.product1, self.product2])
        self.assertEqual(list(response.context['categories']), [self.category])

    def test_shop_view_search_filter(self):
        """Перевірка GET-запиту на сторінку shop із пошуком."""
        response = client.get(reverse('catalog:shop') + '?search=Product 1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['products']), [self.product1])

    def test_shop_view_category_filter(self):
        """Перевірка GET-запиту на сторінку shop із фільтром за категорією."""
        response = client.get(reverse('catalog:shop') + f'?category={self.category.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['products']), [self.product1, self.product2])

    def test_shop_view_price_filter(self):
        """Перевірка GET-запиту на сторінку shop із фільтром за ціною."""
        response = client.get(reverse('catalog:shop') + '?price_min=120&price_max=140')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['products']), [])  # Жоден продукт не підходить

