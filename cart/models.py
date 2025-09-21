from django.db import models
from django.conf import settings
from menu.models import Item

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.item.name} x {self.quantity}"

    def total_price(self):
        return self.item.price * self.quantity
