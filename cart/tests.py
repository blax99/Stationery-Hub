from django.test import TestCase, override_settings


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class SignedOutCartPageTests(TestCase):
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
