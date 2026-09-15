from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # All products catalog: /products/
    path('', views.product_list, name='product_list'),
    
    # Category filter route (Name updated to category_detail): /products/category/<slug>/
    path('category/<slug:category_slug>/', views.product_list, name='category_detail'),
    
    # Single product detail route: /products/<slug>/
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]