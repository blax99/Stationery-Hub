from django.urls import path
from .views import cart
from . import views

urlpatterns = [
    path("", cart, name="cart"),
    path("wishlist/", views.wishlist, name = "wishlist"),
]