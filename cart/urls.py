from django.urls import path
from .views import cart
from . import views

urlpatterns = [
    path("", cart, name="cart"),
    path("wishlist/", views.wishlist, name = "wishlist"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path( "update/<int:item_id>/", views.update_cart_quantity,name="update_cart_quantity"),
]