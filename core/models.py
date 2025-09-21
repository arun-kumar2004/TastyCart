from django.contrib.auth.models import AbstractUser
from django.db import models

USER_TYPE_CHOICES = (
    ("customer", "Customer"),
    ("service_provider", "Service Provider"),
    ("admin", "Admin"),
)

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default="customer")
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    last_name = None


    def is_customer(self):
        return self.user_type == "customer"

    def is_service_provider(self):
        return self.user_type == "service_provider"

    def is_admin_user(self):
        return self.user_type == "admin"

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.user_type = "admin"
        super().save(*args, **kwargs)
