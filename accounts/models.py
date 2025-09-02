from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    auth_code = models.CharField(max_length=6, null=True, blank=True)
    auth_expires_at = models.DateTimeField(null=True, blank=True)

