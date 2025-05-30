import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from .models import CustomUser

# Ініціалізація тестового клієнта
client = Client()

# Отримуємо модель користувача
CustomUser = get_user_model()

class CustomUserModelTest(TestCase):
    def setUp(self):
        """Створюємо тестового користувача перед кожним тестом."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone='12345678901',
            address='Test Address'
        )

    def test_custom_user_creation(self):
        """Перевірка створення користувача."""
        self.assertEqual(str(self.user), 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.phone, '12345678901')
        self.assertEqual(self.user.address, 'Test Address')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_custom_user_fields_blank(self):
        """Перевірка, що поля phone і address можуть бути порожніми."""
        user = CustomUser.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.assertIsNone(user.phone)
        self.assertIsNone(user.address)

class CustomUserCreationFormTest(TestCase):
    def test_form_valid_data(self):
        """Перевірка валідності форми з коректними даними."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone': '09876543210',
            'address': 'New Address',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_password_match(self):
        """Перевірка, що форма не валідна, якщо паролі не збігаються."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone': '09876543210',
            'address': 'New Address',
            'password1': 'newpass123',
            'password2': 'wrongpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_email_required(self):
        """Перевірка, що email є обов'язковим полем."""
        form_data = {
            'username': 'newuser',
            'phone': '09876543210',
            'address': 'New Address',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class UserViewsTest(TestCase):
    def setUp(self):
        """Створюємо тестового користувача перед кожним тестом."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')
        self.home_url = reverse('main:home')

    def test_register_view_get(self):
        """Перевірка GET-запиту на сторінку реєстрації."""
        response = client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_register_view_post_success(self):
        """Перевірка POST-запиту на реєстрацію з валідними даними."""
        form_data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'phone': '09876543210',
            'address': 'New Address',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = client.post(self.register_url, form_data)
        self.assertRedirects(response, self.home_url)
        self.assertTrue(CustomUser.objects.filter(username='newuser2').exists())

    def test_register_view_post_invalid(self):
        """Перевірка POST-запиту на реєстрацію з невалідними даними."""
        form_data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'phone': '09876543210',
            'address': 'New Address',
            'password1': 'newpass123',
            'password2': 'wrongpass123'
        }
        response = client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertFalse(CustomUser.objects.filter(username='newuser2').exists())

    def test_login_view_get(self):
        """Перевірка GET-запиту на сторінку логіну."""
        response = client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_view_post_success(self):
        """Перевірка POST-запиту на логін з валідними даними."""
        response = client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, self.home_url)
        self.assertTrue('_auth_user_id' in client.session)

    def test_login_view_post_invalid(self):
        """Перевірка POST-запиту на логін з невалідними даними."""
        response = client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertFalse('_auth_user_id' in client.session)

    def test_logout_view(self):
        """Перевірка виходу з акаунта."""
        client.login(username='testuser', password='testpass123')
        response = client.get(self.logout_url)
        self.assertRedirects(response, self.home_url)
        self.assertFalse('_auth_user_id' in client.session)
