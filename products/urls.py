from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
<<<<<<< HEAD
    # All products catalog: /products/
    path('', views.product_list, name='product_list'),
    
    # Category filter routes
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),

    # Categories index route (Fixes the NoReverseMatch error for 'category_list')
    path('categories/', views.product_list, name='category_list'),
    
    # Single product detail route: /products/<slug>/
=======
    # All products page: /products/
    path('', views.product_list, name='product_list'),
    
    # Filter products by category slug: /products/category/<category_slug>/
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    
    # Single product detail page: /products/<slug>/
>>>>>>> d4b1eff9dab1543a61c27987199b640967670139
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]