from html import unescape
from unittest.mock import patch
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/users/register/"

    @patch("users.views.send_mail")
    def test_register_success(self, send_mail):
        data = {
            "username": "testuser1",
            "email": "testuser1@example.com",
            "password": "TestPass123",
            "phone_number": "9800000001",
            "role": "customer",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="testuser1@example.com").exists())
        send_mail.assert_called_once()

    @patch("users.views.send_mail", side_effect=TimeoutError("SMTP timed out"))
    def test_registration_succeeds_if_verification_email_times_out(self, send_mail):
        data = {
            "username": "testuser-timeout",
            "email": "timeout@example.com",
            "password": "TestPass123",
        }

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="timeout@example.com").exists())
        send_mail.assert_called_once()

    def test_register_duplicate_email(self):
        User.objects.create_user(
            username="existing", email="dup@example.com", password="TestPass123"
        )
        data = {
            "username": "newuser",
            "email": "dup@example.com",
            "password": "TestPass123",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_phone(self):
        data = {
            "username": "testuser2",
            "email": "testuser2@example.com",
            "password": "TestPass123",
            "phone_number": "123",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class PasswordResetRequestTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.reset_url = "/users/password-reset/"
        self.user = User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="TestPass123",
        )

    @override_settings(SITE_URL="https://stationery.example")
    def test_password_reset_request_sends_decorated_email_with_working_reset_link(self):
        response = self.client.post(
            self.reset_url, {"email": self.user.email}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"], "If this email exists, a reset link has been sent."
        )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Reset your Stationery Hub password")
        self.assertEqual(email.to, [self.user.email])
        self.assertEqual(len(email.alternatives), 1)
        self.assertEqual(email.alternatives[0].mimetype, "text/html")
        self.assertIn("Reset my password", email.alternatives[0].content)
        self.assertIn("Hello resetuser", email.body)

        reset_link = unescape(
            email.alternatives[0].content.split('href="', 1)[1].split('"', 1)[0]
        )
        reset_path = urlsplit(reset_link)
        self.assertEqual(reset_path.netloc, "stationery.example")
        self.assertEqual(reset_path.scheme, "https")
        response = self.client.get(f"{reset_path.path}?{reset_path.query}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Choose a new password")

    @patch(
        "users.views.EmailMultiAlternatives.send",
        side_effect=TimeoutError("SMTP timed out"),
    )
    def test_password_reset_request_succeeds_if_email_times_out(self, send_email):
        response = self.client.post(
            self.reset_url, {"email": self.user.email}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"], "If this email exists, a reset link has been sent."
        )
        send_email.assert_called_once()

    @patch("users.views.EmailMultiAlternatives")
    def test_password_reset_request_does_not_send_for_unknown_email(self, email_class):
        response = self.client.post(
            self.reset_url, {"email": "unknown@example.com"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"], "If this email exists, a reset link has been sent."
        )
        email_class.assert_not_called()


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="reset-confirm-user",
            email="reset-confirm@example.com",
            password="OriginalPassword123!",
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.confirm_url = (
            f"/users/password-reset-confirm/?uid={self.uid}&token={self.token}"
        )

    def test_reset_link_opens_password_form(self):
        response = self.client.get(self.confirm_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="reset-password-form"')
        self.assertContains(response, "Choose a new password")

    def test_invalid_reset_link_shows_recovery_action(self):
        response = self.client.get(
            f"/users/password-reset-confirm/?uid={self.uid}&token=invalid"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reset link unavailable")
        self.assertContains(response, "Request a new link")
        self.assertNotContains(response, 'id="reset-password-form"')

    def test_valid_reset_link_updates_password(self):
        response = self.client.post(
            "/users/password-reset-confirm/",
            {
                "uid": self.uid,
                "token": self.token,
                "new_password": "NewStrongPassword456!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPassword456!"))

    def test_reset_rejects_weak_password(self):
        response = self.client.post(
            "/users/password-reset-confirm/",
            {
                "uid": self.uid,
                "token": self.token,
                "new_password": "short",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OriginalPassword123!"))


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = "/users/login/"
        self.user = User.objects.create_user(
            username="loginuser", email="login@example.com", password="TestPass123"
        )

    def test_login_success(self):
        response = self.client.post(
            self.login_url, {"email": "login@example.com", "password": "TestPass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["role"], "customer")

    def test_login_wrong_password(self):
        response = self.client.post(
            self.login_url, {"email": "login@example.com", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_sign_in_rejects_customer_accounts(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "login@example.com",
                "password": "TestPass123",
                "admin_only": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "This account does not have admin access."
        )

    def test_admin_sign_in_accepts_admin_accounts(self):
        self.user.role = "admin"
        self.user.save(update_fields=["role"])

        response = self.client.post(
            self.login_url,
            {
                "email": "login@example.com",
                "password": "TestPass123",
                "admin_only": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "admin")

    def test_admin_sign_in_accepts_django_superusers(self):
        self.user.is_superuser = True
        self.user.save(update_fields=["is_superuser"])

        response = self.client.post(
            self.login_url,
            {
                "email": "login@example.com",
                "password": "TestPass123",
                "admin_only": True,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "admin")


class ProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="TestPass123",
        )
        self.client.force_authenticate(self.user)

    def test_profile_can_save_order_shipping_details(self):
        response = self.client.patch(
            "/users/profile/",
            {
                "first_name": "Profile",
                "last_name": "User",
                "phone_number": "9800000000",
                "address": "1 Stationery Street",
                "city": "Kathmandu",
                "postal_code": "44600",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Profile")
        self.assertEqual(self.user.last_name, "User")
        self.assertEqual(self.user.phone_number, "9800000000")
        self.assertEqual(self.user.address, "1 Stationery Street")
        self.assertEqual(self.user.city, "Kathmandu")
        self.assertEqual(self.user.postal_code, "44600")

    def test_profile_page_uses_wide_layout_and_single_full_name_field(self):
        response = self.client.get("/users/profile-page/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'id="full_name"')
        self.assertContains(response, "max-w-4xl")
        self.assertContains(response, 'class="profile-form"')
        self.assertContains(response, "column-gap: 2rem")
        self.assertContains(response, "max-width: 24rem")
        self.assertContains(response, "profile-save")
        self.assertNotContains(response, 'id="first_name"')
        self.assertNotContains(response, 'id="last_name"')


class LoginPageTests(TestCase):
    def test_admin_sign_in_does_not_show_the_admin_access_helper(self):
        response = self.client.get("/users/login-page/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in as Admin")
        self.assertContains(response, 'id="login-form"')
        self.assertNotContains(
            response,
            "Your account must already have Admin access.",
        )
        self.assertContains(response, "stationery-notification")
        self.assertContains(response, "Admin login successful.")
        self.assertContains(response, "Login successful.")
        self.assertContains(response, "right: 1rem")
        self.assertContains(response, "{ reload: true }")
