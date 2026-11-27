from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings, override_settings
from django.urls import reverse
from django.utils import timezone

from cart.models import Cart, CartItem
from products.models import Category, Products

from .models import Order, OrderItem, ShippingAddress


class CheckoutFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="checkout-user",
            email="checkout@example.com",
            password="TestPass123",
        )
        self.category = Category.objects.create(name="Notebooks")
        self.product = Products.objects.create(
            category=self.category,
            name="Test notebook",
            description="A test product",
            price=Decimal("25.00"),
            stock=5,
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.client.force_login(self.user)

    def test_proceed_to_checkout_renders_checkout_page(self):
        response = self.client.get(reverse("checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Checkout")
        self.assertContains(response, "Test notebook")

    def test_checkout_prefills_saved_shipping_profile(self):
        self.user.first_name = "Checkout"
        self.user.last_name = "User"
        self.user.address = "1 Stationery Street"
        self.user.city = "Kathmandu"
        self.user.postal_code = "44600"
        self.user.phone_number = "9800000000"
        self.user.save()

        response = self.client.get(reverse("checkout"))

        self.assertContains(response, 'value="Checkout User"')
        self.assertContains(response, "1 Stationery Street")
        self.assertContains(response, 'value="Kathmandu"')
        self.assertContains(response, 'value="44600"')
        self.assertContains(response, 'value="9800000000"')

    def test_order_history_renders_existing_orders(self):
        order = Order.objects.create(user=self.user, total_amount=Decimal("50.00"))

        response = self.client.get(reverse("order_history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Order #{order.id:04d}")

    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
    )
    def test_order_confirmation_uses_in_page_dialog_for_cancellation(self):
        self.user.is_email_verified = True
        self.user.save(update_fields=["is_email_verified"])
        order = Order.objects.create(user=self.user, total_amount=Decimal("50.00"))

        response = self.client.get(
            reverse("order_confirmation", kwargs={"order_id": order.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="cancel-confirmation-dialog"')
        self.assertContains(response, "Yes, Cancel Order")
        self.assertNotContains(response, "confirm(")

    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
    )
    def test_empty_order_history_links_to_products(self):
        self.user.is_email_verified = True
        self.user.save(update_fields=["is_email_verified"])

        response = self.client.get(reverse("order_history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No orders yet")
        self.assertContains(response, "Browse our stationery collection")
        self.assertContains(response, reverse("products:product_list"))
        self.assertContains(response, "order-action order-action-primary")

    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
    )
    def test_active_order_progress_step_is_green_in_dark_mode(self):
        self.user.is_email_verified = True
        self.user.save(update_fields=["is_email_verified"])
        Order.objects.create(user=self.user, total_amount=Decimal("50.00"))

        response = self.client.get(reverse("order_history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "order-progress-step-active")
        self.assertContains(response, ".dark .order-progress-step-active")
        self.assertContains(response, "background: #16a34a;")

    def test_place_order_creates_order_and_clears_cart(self):
        response = self.client.post(
            reverse("checkout"),
            {
                "full_name": "Checkout User",
                "email": self.user.email,
                "address": "1 Stationery Street",
                "city": "Kathmandu",
                "postal_code": "44600",
                "phone": "9800000000",
            },
        )

        order = Order.objects.get(user=self.user)
        self.assertRedirects(
            response,
            reverse("order_confirmation", kwargs={"order_id": order.id}),
        )
        self.assertEqual(order.total_amount, Decimal("50.00"))
        self.assertEqual(OrderItem.objects.filter(order=order).count(), 1)
        self.assertEqual(
            ShippingAddress.objects.get(order=order).full_name, "Checkout User"
        )
        self.assertEqual(
            ShippingAddress.objects.get(order=order).postal_code, "44600"
        )
        self.assertFalse(self.cart.items.exists())

        confirmation_response = self.client.get(response.url)
        self.assertEqual(confirmation_response.status_code, 200)
        delivery_start = timezone.localdate(order.created_at) + timedelta(days=3)
        delivery_end = timezone.localdate(order.created_at) + timedelta(days=5)
        self.assertContains(
            confirmation_response,
            f"{delivery_start.strftime('%B %d, %Y')} - "
            f"{delivery_end.strftime('%B %d, %Y')}",
        )
