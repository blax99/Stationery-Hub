from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Order

User = get_user_model()


class OrderAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123"
        )

    def test_list_orders_requires_auth(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_orders_authenticated_empty(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_create_order_authenticated(self):
        self.client.force_authenticate(user=self.user)
        payload = {"total_amount": "150.00", "status": "pending"}
        response = self.client.post("/api/orders/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().user, self.user)

    def test_create_order_unauthenticated(self):
        payload = {"total_amount": "150.00", "status": "pending"}
        response = self.client.post("/api/orders/", payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)