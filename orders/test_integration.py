from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Category, Products
from orders.models import Order
from cart.models import Cart, CartItem


class FullPurchaseFlowIntegrationTest(APITestCase):
    """
    Integration test simulating a real customer journey across
    Auth -> Products -> Cart -> Orders, using a real JWT token
    (not force_authenticate), to confirm the modules work together
    end to end, not just individually.
    """

    def setUp(self):
        self.category, _ = Category.objects.get_or_create(name="Pens & Writing")
        self.product = Products.objects.create(
            category=self.category,
            name="Integration Test Pen",
            description="Used only in integration test",
            price="45.00",
            stock=50,
        )

    def test_full_purchase_flow(self):
        # 1. Register a new user
        register_payload = {
            "username": "integration_user",
            "email": "integration_user@example.com",
            "password": "TestPass123",
            "phone_number": "9812345678",
            "role": "customer",
        }
        register_response = self.client.post("/api/users/register/", register_payload)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # 2. Log in as that user to get a real JWT token
        login_payload = {
            "email": "integration_user@example.com",
            "password": "TestPass123",
        }
        login_response = self.client.post("/api/users/login/", login_payload)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data.get("access") or login_response.data.get("token")
        self.assertIsNotNone(access_token, "Login response did not include an access token")

        # Attach the real token to every request from here on
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # 3. Browse products
        products_response = self.client.get("/api/products/")
        self.assertEqual(products_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(products_response.data), 1)

        # 4. Add a product to the cart
        add_to_cart_response = self.client.post(
            "/api/cart/items/",
            {"product_id": self.product.id, "quantity": 2},
        )
        self.assertEqual(add_to_cart_response.status_code, status.HTTP_201_CREATED)

        # 5. Confirm the cart reflects the added item
        cart_response = self.client.get("/api/cart/")
        self.assertEqual(cart_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(cart_response.data["items"]), 1)

        # 6. Place an order
        order_payload = {"total_amount": "90.00", "status": "pending"}
        order_response = self.client.post("/api/orders/", order_payload)
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)

        # 7. Confirm the order now shows up when listing this user's orders
        list_orders_response = self.client.get("/api/orders/")
        self.assertEqual(list_orders_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_orders_response.data), 1)
        self.assertEqual(list_orders_response.data[0]["total_amount"], "90.00")

        # Sanity check directly against the database too
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Cart.objects.get(user__email="integration_user@example.com").items.count(), 1)