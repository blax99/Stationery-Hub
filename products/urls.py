from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # All products catalog: /products/
    path('', views.product_list, name='product_list'),

    # Filter products by category slug: /products/category/<category_slug>/
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),

    # Categories index route (fixes the NoReverseMatch error for 'category_list')
    path('categories/', views.product_list, name='category_list'),

    # Single product detail page: /products/<slug>/
    # Keep this last, so "categories" isn't mistaken for a product slug
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]