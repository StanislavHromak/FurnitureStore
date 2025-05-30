from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Product, Category
from django.core.files.base import ContentFile

client = Client()

class MainViewsTest(TestCase):
    def setUp(self):
        """Створюємо тестові об'єкти перед кожним тестом."""
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        test_image = ContentFile(b"dummy image data", name="test_image.jpg")
        self.product1 = Product.objects.create(
            name='Product 1',
            slug='product-1',
            category=self.category,
            price=100.00,
            description='Description 1',
            is_featured=True,
            quantity=5,
            image=test_image
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            slug='product-2',
            category=self.category,
            price=150.00,
            description='Description 2',
            is_featured=True,
            quantity=3,
            image=test_image
        )
        self.product3 = Product.objects.create(
            name='Product 3',
            slug='product-3',
            category=self.category,
            price=200.00,
            description='Description 3',
            is_featured=False,
            quantity=2,
            image=test_image
        )

    def test_home_view(self):
        """Перевірка GET-запиту на сторінку home."""
        response = client.get(reverse('main:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')
        chunked_products = response.context['chunked_products']
        self.assertEqual(len(chunked_products), 1)
        self.assertEqual(len(chunked_products[0]), 2)

    def test_about_view(self):
        """Перевірка GET-запиту на сторінку about."""
        response = client.get(reverse('main:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/about.html')

    def test_design_view(self):
        """Перевірка GET-запиту на сторінку design."""
        response = client.get(reverse('main:design'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/design.html')
        products = response.context['products']
        self.assertEqual(len(products), 3)

