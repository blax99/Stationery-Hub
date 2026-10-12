from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/users/register/"

    def test_register_success(self):
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
