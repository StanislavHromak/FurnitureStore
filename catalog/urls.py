from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # Змінюємо на <int:product_id>
    path('featured_products/', views.featured_products, name='featured_products'),
]