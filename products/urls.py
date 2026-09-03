from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # All products page: /products/
    path('', views.product_list, name='product_list'),
    
    # Filter products by category slug: /products/category/<category_slug>/
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    
    # Single product detail page: /products/<slug>/
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]