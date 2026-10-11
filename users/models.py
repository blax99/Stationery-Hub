from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    is_email_verified = models.BooleanField(default=False)

    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("admin", "Admin"),
        ("vendor", "Vendor"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="customer")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
