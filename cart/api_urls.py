from django.urls import path
from .api_views import (
    CartDetailView,
    CartItemCreateView,
    CartItemDetailView,
    WishlistDetailView,
    WishlistItemCreateView,
    WishlistItemDetailView,
)

app_name = 'cart_api'

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart-detail'),
    path('items/', CartItemCreateView.as_view(), name='cart-item-create'),
    path('items/<int:pk>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    path('wishlist/', WishlistDetailView.as_view(), name='wishlist-detail'),
    path('wishlist/items/', WishlistItemCreateView.as_view(), name='wishlist-item-create'),
    path('wishlist/items/<int:pk>/', WishlistItemDetailView.as_view(), name='wishlist-item-detail'),
]