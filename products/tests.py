from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Products


class ProductAPITests(APITestCase):
    def setUp(self):
        self.category, _ = Category.objects.get_or_create(name="Pens & Writing")
        self.product = Products.objects.create(
            category=self.category,
            name="Blue Gel Pen",
            description="Smooth writing pen",
            price="45.00",
            stock=50,
        )

    def test_list_products(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_product_detail(self):
        response = self.client.get(f"/api/products/{self.product.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Blue Gel Pen")

    def test_list_categories(self):
        response = self.client.get("/api/products/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_product(self):
        payload = {
            "name": "Red Gel Pen",
            "description": "Red version",
            "price": "45.00",
            "stock": 30,
            "is_available": True,
            "category_id": self.category.id,
        }
        response = self.client.post("/api/products/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)