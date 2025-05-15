from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва")
    slug = models.SlugField(unique=True, verbose_name="Слаг")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва")
    slug = models.SlugField(unique=True, verbose_name="Слаг", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категорія")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Зображення")
    description = models.TextField(verbose_name="Опис")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендований")
    stock = models.PositiveIntegerField(default=0, verbose_name="На складі")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return self.name