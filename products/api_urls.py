from django.urls import path
from .api_views import (
    CategoryListCreateView,
    ProductListCreateView,
    ProductDetailView,
)

app_name = 'products_api'

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    
]
