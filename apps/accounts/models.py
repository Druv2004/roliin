from django.db import models
from django.contrib.auth.models import AbstractUser

# ================================ ACCOUNTS MODELS ==================================
class Account(AbstractUser):
    email = models.EmailField(unique=True)
    reset_code = models.CharField(max_length=6, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

