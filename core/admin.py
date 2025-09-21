from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "email", "user_type", "is_staff", "is_active"]
    list_filter = ["user_type", "is_staff", "is_active"]
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "address")}),
        ("Permissions", {"fields": ("user_type", "is_staff", "is_active", "groups", "user_permissions")}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
