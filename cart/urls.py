from django.urls import path
from .views import cart, CartAPIView
from . import views

urlpatterns = [
    path("", cart, name="cart"),
    path("items/", CartAPIView.as_view(), name="cart-api"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("update/<int:item_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("delete/<int:item_id>/", views.delete_cart_item, name="delete_cart_item"),
    path("wishlist/remove/<int:item_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
]