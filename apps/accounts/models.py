from django.db import models
from django.contrib.auth.models import AbstractUser

# ================================ ACCOUNTS MODELS ==================================
class Account(AbstractUser):
    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("STAFF", "Staff"),
    )

    email = models.EmailField(unique=True)
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="STAFF")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
