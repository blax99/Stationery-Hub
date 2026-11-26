from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cart.models import Cart, CartItem
from orders.models import Order
from products.models import Category, Products


class ChatbotReplyTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Writing")
        self.product = Products.objects.create(
            category=self.category,
            name="Blue ballpoint pen",
            description="A smooth-writing blue pen.",
            price="12.50",
            stock=3,
        )
        self.user = get_user_model().objects.create_user(
            username="chat-customer",
            email="chat@example.com",
            password="test-password",
            is_email_verified=True,
        )

    def ask(self, message):
        return self.client.post(reverse("chat_reply"), {"message": message})

    def test_product_question_reads_current_catalog_data(self):
        response = self.ask("How much is the blue ballpoint pen?")
        reply = response.json()["reply"]

        self.assertEqual(response.status_code, 200)
        self.assertTrue(reply.startswith("In-stock products:\n\n[1] Blue ballpoint pen"))
        self.assertIn(
            "Category: Writing | Price: Rs. 12.50 | Stock: 3 | "
            "Description: A smooth-writing blue pen.",
            reply,
        )

    def test_product_reply_adds_a_final_period_to_unpunctuated_descriptions(self):
        self.product.description = "A blue pen for everyday writing"
        self.product.save(update_fields=["description"])

        response = self.ask("Tell me about the blue pen")

        self.assertIn(
            "Description: A blue pen for everyday writing.",
            response.json()["reply"],
        )

    def test_product_search_can_use_a_specific_name_without_saying_product(self):
        Products.objects.create(
            category=self.category,
            name="Red stapler",
            description="A compact stapler.",
            price="40.00",
            stock=2,
        )

        response = self.ask("How much is the red stapler?")

        self.assertIn("Red stapler", response.json()["reply"])
        self.assertIn("Rs. 40.00", response.json()["reply"])

    def test_product_listing_ignores_listing_and_question_words(self):
        for question in ("Show all products", "Where can I find products?"):
            with self.subTest(question=question):
                response = self.ask(question)

                self.assertIn("Blue ballpoint pen", response.json()["reply"])

    def test_plural_product_search_matches_singular_catalog_names(self):
        response = self.ask("Show me pens")

        self.assertIn("Blue ballpoint pen", response.json()["reply"])

    def test_cart_question_shows_only_signed_in_users_cart(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.client.force_login(self.user)

        response = self.ask("What's in my cart?")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Blue ballpoint pen x 2", response.json()["reply"])
        self.assertIn("Rs. 25.00", response.json()["reply"])

    def test_orders_require_login_and_are_limited_to_the_signed_in_user(self):
        own_order = Order.objects.create(user=self.user, total_amount="25.00")
        other_user = get_user_model().objects.create_user(
            username="another-customer",
            email="another@example.com",
            password="test-password",
        )
        other_order = Order.objects.create(user=other_user, total_amount="99.00")

        anonymous_reply = self.ask("What is my order status?").json()["reply"]
        self.assertIn("sign in", anonymous_reply)

        self.client.force_login(self.user)
        response = self.ask("What is the status of order #%s?" % own_order.id)

        self.assertIn(f"Order #{own_order.id:04d}", response.json()["reply"])
        self.assertNotIn(f"Order #{other_order.id:04d}", response.json()["reply"])

    def test_unverified_customer_cannot_view_order_details(self):
        self.user.is_email_verified = False
        self.user.save(update_fields=["is_email_verified"])
        self.client.force_login(self.user)

        response = self.ask("What is my order status?")

        self.assertIn("verify your email", response.json()["reply"])

    def test_generic_payment_question_explains_khalti_checkout_flow(self):
        response = self.ask("How can I pay?")

        self.assertIn("Khalti", response.json()["reply"])
        self.assertIn("order confirmation page", response.json()["reply"])

    def test_about_question_describes_the_stationery_website(self):
        response = self.ask("Tell me about this website")

        self.assertIn("online store", response.json()["reply"])
        self.assertIn("stationery", response.json()["reply"])

    def test_empty_question_is_rejected(self):
        response = self.ask("   ")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["reply"], "Please enter a question.")
