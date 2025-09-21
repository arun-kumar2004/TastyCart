# menu/admin.py
from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "popular", "created_by", "created_at")
    list_filter = ("category", "popular")
    search_fields = ("name", "description")
