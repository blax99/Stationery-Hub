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
