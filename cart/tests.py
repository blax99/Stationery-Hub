from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Category, Products
from .models import Cart, Wishlist

User = get_user_model()


class CartWishlistAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123"
        )
        self.category, _ = Category.objects.get_or_create(name="Pens & Writing")
        self.product = Products.objects.create(
            category=self.category,
            name="Blue Gel Pen",
            description="Smooth writing pen",
            price="45.00",
            stock=50,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_cart_auto_creates(self):
        response = self.client.get("/api/cart/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)

    def test_add_item_to_cart(self):
        payload = {"product_id": self.product.id, "quantity": 2}
        response = self.client.post("/api/cart/items/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_wishlist_auto_creates(self):
        response = self.client.get("/api/cart/wishlist/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Wishlist.objects.filter(user=self.user).count(), 1)

    def test_add_item_to_wishlist(self):
        payload = {"product_id": self.product.id}
        response = self.client.post("/api/cart/wishlist/items/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cart_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/cart/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)