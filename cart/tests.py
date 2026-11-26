from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class CartPageTests(TestCase):
    def test_navbar_uses_theme_toggle_instead_of_search_input(self):
        response = self.client.get("/cart/")

        self.assertContains(response, 'id="theme-toggle"')
        self.assertNotContains(response, 'id="searchInput"')

    def test_cart_page_prompts_signed_out_visitors_to_log_in(self):
        response = self.client.get("/cart/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in to view your cart")
        self.assertContains(response, "/users/login-page/?next=/cart/")
        self.assertNotContains(response, "Loading cart...")

    def test_wishlist_page_prompts_signed_out_visitors_to_log_in(self):
        response = self.client.get("/wishlist/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in to view your wishlist")
        self.assertContains(response, "/users/login-page/?next=/wishlist/")
        self.assertNotContains(response, "Loading wishlist...")

    def test_cart_and_wishlist_primary_buttons_share_dark_mode_colors(self):
        user = get_user_model().objects.create_user(
            email="cart-theme@example.com",
            username="cart-theme",
            password="test-password",
        )
        self.client.force_login(user)

        cart_response = self.client.get("/cart/")
        wishlist_response = self.client.get("/wishlist/")

        self.assertContains(cart_response, 'class="rounded-md border')

        for response in (cart_response, wishlist_response):
            self.assertContains(response, "dark:bg-red-800")
            self.assertContains(response, "dark:hover:bg-red-700")
            self.assertContains(response, "rounded-md")

    def test_authenticated_wishlist_page_loads_without_obsolete_token_check(self):
        user = get_user_model().objects.create_user(
            email="wishlist-theme@example.com",
            username="wishlist-theme",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get("/wishlist/")

        self.assertContains(response, 'window.stationeryApiFetch("/wishlist/api/")')
        self.assertNotContains(response, "if (!token)")
