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
        self.register_url = '/api/users/register/'

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
        User.objects.create_user(username="existing", email="dup@example.com", password="TestPass123")
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
        self.login_url = '/api/users/login/'
        self.user = User.objects.create_user(
            username="loginuser", email="login@example.com", password="TestPass123"
        )

    def test_login_success(self):
        response = self.client.post(self.login_url, {"email": "login@example.com", "password": "TestPass123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(self.login_url, {"email": "login@example.com", "password": "wrongpass"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)