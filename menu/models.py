# menu/models.py
from django.db import models
from django.conf import settings

CATEGORY_CHOICES = (
    ("Dish", "Dish"),
    ("Sweet", "Sweet"),
)

def item_image_upload_to(instance, filename):
    # store in media/items/<id or timestamp>_filename
    return f"items/{instance.name}_{filename}"

class Item(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Dish")
    image = models.ImageField(upload_to=item_image_upload_to, blank=True, null=True)
    popular = models.BooleanField(default=False, help_text="If checked, item will appear on home popular section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self):
        return self.name
