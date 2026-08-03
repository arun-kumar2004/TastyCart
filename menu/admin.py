# menu/admin.py
from django.contrib import admin
from .models import Item, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "popular",
        "created_by",
        "created_at",
    )

    list_filter = (
        "category",
        "popular",
    )

    search_fields = (
        "name",
        "description",
    )