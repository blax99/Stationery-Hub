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
        self.assertContains(
            response,
            'id="cart-count"\n            class="absolute -top-2 -right-2 min-w-4 h-4 px-1 bg-blue-600 text-white rounded-full text-[10px] flex items-center justify-center"',
        )

    def test_mobile_account_controls_have_dark_mode_contrast(self):
        response = self.client.get("/wishlist/")

        self.assertContains(
            response,
            'class="account-name overflow-hidden min-w-0 max-w-32 truncate text-gray-800 dark:text-gray-100"',
        )
        self.assertContains(
            response,
            'class="account-chevron fa-solid fa-chevron-down text-xs text-gray-500 dark:text-gray-300 transition-transform"',
        )
        self.assertContains(
            response,
            "text-gray-700 dark:text-gray-100 transition hover:bg-gray-50 dark:hover:bg-gray-700",
        )

    def test_cart_page_prompts_signed_out_visitors_to_log_in(self):
        response = self.client.get("/cart/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in to view your cart")
        self.assertContains(response, "mt-6 inline-block rounded-md border")
        self.assertContains(response, "dark:bg-red-800")
        self.assertContains(response, "/users/login-page/?next=/cart/")
        self.assertNotContains(response, "Loading cart...")

    def test_wishlist_page_prompts_signed_out_visitors_to_log_in(self):
        response = self.client.get("/wishlist/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in to view your wishlist")
        self.assertContains(
            response,
            "mt-6 inline-block rounded-md bg-slate-800 dark:bg-red-800",
        )
        self.assertContains(response, "dark:hover:bg-red-700")
        self.assertContains(response, "wishlist-empty-heart")
        self.assertContains(response, 'fill="none"')
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

        self.assertContains(
            cart_response,
            "rounded-md border border-slate-800 dark:border-red-800",
        )

        for response in (cart_response, wishlist_response):
            self.assertContains(response, "dark:bg-red-800")
            self.assertContains(response, "dark:hover:bg-red-700")
            self.assertContains(response, "rounded-md")

        self.assertContains(wishlist_response, "wishlist-remove-icon")
        self.assertContains(wishlist_response, 'd="M6 6l12 12M18 6 6 18"')
        self.assertContains(wishlist_response, "h-8 w-8 items-center justify-center rounded-full")
        self.assertContains(wishlist_response, "rounded-xl overflow-hidden relative")
        self.assertContains(
            wishlist_response,
            "inline-block rounded-md bg-slate-800 dark:bg-red-800",
        )
        self.assertContains(wishlist_response, "dark:border-transparent")
        self.assertContains(wishlist_response, "dark:bg-black")
        self.assertContains(wishlist_response, "dark:hover:bg-gray-950")
        self.assertContains(wishlist_response, 'class="wishlist-remove-icon h-4 w-4"')
        self.assertContains(wishlist_response, 'stroke-width="2.5"')
        self.assertContains(wishlist_response, 'fill="none"')
        self.assertContains(wishlist_response, "aria-label=\"Remove from wishlist\"")

    def test_authenticated_wishlist_page_loads_without_obsolete_token_check(self):
        user = get_user_model().objects.create_user(
            email="wishlist-theme@example.com",
            username="wishlist-theme",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get("/wishlist/")

        self.assertContains(response, 'window.stationeryApiFetch("/wishlist/api/")')
        self.assertContains(response, "wishlist-empty-heart")
        self.assertContains(
            response,
            'document.addEventListener("DOMContentLoaded", startWishlistLoad',
        )
        self.assertContains(
            response,
            'document.addEventListener("turbo:load", startWishlistLoad',
        )
        self.assertNotContains(response, "if (!token)")
