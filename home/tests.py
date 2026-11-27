from django.test import TestCase
from django.test import override_settings


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class HomePageThemeTests(TestCase):
    def test_home_background_continues_through_footer_spacing(self):
        response = self.client.get("/")

        self.assertContains(
            response,
            'class="min-h-screen flex flex-col bg-amber-50 dark:bg-gray-900"',
        )

    @override_settings(DEBUG=False)
    def test_unknown_url_uses_custom_404_page(self):
        response = self.client.get("/not-a-real-page/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "This page is off the page.", status_code=404)
        self.assertContains(response, "Browse products", status_code=404)

    @override_settings(DEBUG=True)
    def test_unknown_url_uses_django_debug_404_page(self):
        response = self.client.get("/not-a-real-page/")

        self.assertEqual(response.status_code, 404)
        self.assertNotContains(
            response, "This page is off the page.", status_code=404
        )

    @override_settings(DEBUG=True)
    def test_view_raised_404_uses_django_debug_page(self):
        response = self.client.get("/products/not-a-real-product/")

        self.assertEqual(response.status_code, 404)
        self.assertNotContains(
            response, "This page is off the page.", status_code=404
        )
